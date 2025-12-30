"""
Adaptadores personalizados para django-allauth que requieren aprobación manual
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import UserRegistrationRequest


class AccountAdapter(DefaultAccountAdapter):
    """
    Adaptador para cuentas regulares (formulario manual)
    Mantiene el comportamiento existente
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Sobrescribir para prevenir que se creen usuarios directamente
        El usuario se crea solo cuando se aprueba la solicitud
        """
        # No crear el usuario directamente, manejar a través de UserRegistrationRequest
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptador para cuentas sociales que requiere aprobación manual
    """
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Permitir el proceso de registro social para crear solicitudes pendientes
        """
        return True
    
    def pre_social_login(self, request, sociallogin):
        """
        Se ejecuta antes del login social
        Verificar si el usuario ya existe o tiene solicitud pendiente
        """
        # Si el usuario ya está conectado a una cuenta social, continuar
        if sociallogin.is_existing:
            return
        
        email = sociallogin.account.extra_data.get('email')
        if not email:
            messages.error(request, 'No se pudo obtener el email de tu cuenta de Google.')
            raise ImmediateHttpResponse(redirect(reverse('account_login')))
        
        # Verificar si ya existe una solicitud pendiente para este email
        existing_request = UserRegistrationRequest.objects.filter(
            email=email, 
            status='pendiente'
        ).first()
        
        if existing_request:
            messages.warning(
                request, 
                f'Ya existe una solicitud pendiente para {email}. '
                'Te contactaremos cuando sea aprobada.'
            )
            raise ImmediateHttpResponse(redirect(reverse('maintenance:registro_exitoso')))
        
        # Verificar si ya existe una solicitud rechazada
        rejected_request = UserRegistrationRequest.objects.filter(
            email=email, 
            status='rechazado'
        ).first()
        
        if rejected_request:
            messages.error(
                request, 
                f'La solicitud para {email} fue previamente rechazada. '
                'Por favor, contacta con el administrador.'
            )
            raise ImmediateHttpResponse(redirect(reverse('account_login')))
    
    def save_user(self, request, sociallogin, form=None):
        """
        En lugar de crear el usuario directamente, crear una UserRegistrationRequest
        """
        # Obtener datos del login social
        email = sociallogin.account.extra_data.get('email')
        first_name = sociallogin.account.extra_data.get('given_name', '')
        last_name = sociallogin.account.extra_data.get('family_name', '')
        google_id = sociallogin.account.uid
        google_picture = sociallogin.account.extra_data.get('picture', '')
        
        # Generar username único basado en el email
        username = self._generate_unique_username(email)
        
        # Crear solicitud de registro pendiente
        registration_request = UserRegistrationRequest.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            registration_type='google',
            google_id=google_id,
            google_picture=google_picture,
            status='pendiente'
        )
        
        # Enviar notificación al administrador
        self._notify_admin(request, registration_request)
        
        # Mostrar mensaje al usuario y redirigir
        messages.success(
            request, 
            f'¡Solicitud de registro con Google enviada! '
            f'Tu solicitud está pendiente de aprobación. '
            f'Te contactaremos a {email} cuando sea procesada.'
        )
        
        # Detener el proceso de login y redirigir
        raise ImmediateHttpResponse(redirect(reverse('maintenance:registro_exitoso')))
    
    def _generate_unique_username(self, email):
        """Generar un username único basado en el email"""
        from django.contrib.auth.models import User
        
        # Usar la parte antes del @ como base
        base_username = email.split('@')[0]
        
        # Limpiar caracteres no válidos
        import re
        base_username = re.sub(r'[^a-zA-Z0-9._-]', '', base_username)
        
        # Asegurar que sea único
        username = base_username
        counter = 1
        
        while (User.objects.filter(username=username).exists() or 
               UserRegistrationRequest.objects.filter(username=username, status='pendiente').exists()):
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def _notify_admin(self, request, solicitud):
        """Enviar notificación al administrador sobre nueva solicitud Google"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            from django.contrib.auth.models import User
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Obtener email del administrador
            try:
                admin_user = User.objects.get(username='sa')
                admin_email = admin_user.email or settings.ADMIN_EMAIL
            except User.DoesNotExist:
                admin_email = settings.ADMIN_EMAIL
            
            subject = f'[Wheeler Keeper] Nueva solicitud Google - {solicitud.username}'
            message = f"""
Hola Administrador,

Se ha recibido una nueva solicitud de registro con Google en Wheeler Keeper.

Detalles del solicitante:
- Tipo de registro: Google OAuth
- Nombre de usuario generado: {solicitud.username}
- Nombre completo: {solicitud.first_name} {solicitud.last_name}
- Email: {solicitud.email}
- Google ID: {solicitud.google_id}
- Fecha de solicitud: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}

Para revisar y aprobar/rechazar esta solicitud, accede al panel de administración:
{request.build_absolute_uri('/admin/maintenance/userregistrationrequest/')}

¡Saludos!
Wheeler Keeper
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
            logger.info(f"Email de notificación Google enviado al admin {admin_email} para solicitud {solicitud.username}")
            
        except Exception as e:
            # Log del error pero continuar
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando email de notificación Google al admin: {e}")
            print(f"Error enviando email de notificación Google al admin: {e}")