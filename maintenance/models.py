from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Vehiculo(models.Model):
    """Modelo para representar un vehículo del usuario"""
    
    TIPOS_VEHICULO = [
        ('moto', 'Moto'),
        ('coche', 'Coche'),
        ('furgoneta', 'Furgoneta'),
        ('autocaravana', 'Autocaravana'),
        ('camion', 'Camión'),
    ]
    
    propietario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Propietario",
        help_text="Usuario propietario del vehículo"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_VEHICULO,
        verbose_name="Tipo de vehículo",
        help_text="Selecciona el tipo de vehículo"
    )
    
    marca = models.CharField(
        max_length=50,
        verbose_name="Marca",
        help_text="Marca del vehículo (ej: BMW, Honda, Mercedes)"
    )
    
    modelo = models.CharField(
        max_length=100,
        verbose_name="Modelo",
        help_text="Modelo específico del vehículo"
    )
    
    año = models.PositiveIntegerField(
        verbose_name="Año de fabricación",
        help_text="Año de fabricación del vehículo",
        null=True,
        blank=True
    )
    
    matricula = models.CharField(
        max_length=20,
        verbose_name="Matrícula",
        help_text="Número de matrícula (opcional)",
        blank=True,
        null=True
    )
    
    kilometraje_actual = models.PositiveIntegerField(
        verbose_name="Kilometraje actual",
        help_text="Kilometraje actual del vehículo",
        default=0
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.marca} {self.modelo}"
    
    def nombre_completo(self):
        """Devuelve el nombre completo del vehículo"""
        año_str = f" {self.año}" if self.año else ""
        return f"{self.marca} {self.modelo}{año_str}"


class TipoMantenimiento(models.Model):
    """Modelo para tipos de mantenimiento predefinidos"""
    
    CATEGORIA_CHOICES = [
        ('motor', 'Motor'),
        ('transmision', 'Transmisión'),
        ('frenos', 'Frenos'), 
        ('neumaticos', 'Neumáticos'),
        ('suspension', 'Suspensión'),
        ('electrico', 'Sistema Eléctrico'),
        ('climatizacion', 'Climatización'),
        ('filtros', 'Filtros'),
        ('otros', 'Otros'),
    ]
    
    VEHICULOS_APLICABLES = [
        ('todos', 'Todos los vehículos'),
        ('moto', 'Solo motos'),
        ('coche', 'Solo coches'),
        ('furgoneta', 'Solo furgonetas'),
        ('autocaravana', 'Solo autocaravanas'),
        ('camion', 'Solo camiones'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del mantenimiento",
        help_text="Ej: Cambio de aceite motor, Cambio filtro aire"
    )
    
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada del mantenimiento",
        blank=True
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        verbose_name="Categoría",
        default='otros'
    )
    
    intervalo_km = models.PositiveIntegerField(
        verbose_name="Intervalo en kilómetros",
        help_text="Cada cuántos kilómetros se debe realizar (0 = no aplica)",
        default=0,
        blank=True
    )
    
    intervalo_meses = models.PositiveIntegerField(
        verbose_name="Intervalo en meses", 
        help_text="Cada cuántos meses se debe realizar (0 = no aplica)",
        default=0,
        blank=True
    )
    
    vehiculos_aplicables = models.CharField(
        max_length=20,
        choices=VEHICULOS_APLICABLES,
        verbose_name="Vehículos aplicables",
        default='todos'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Si está activo aparecerá en las listas"
    )
    
    class Meta:
        verbose_name = "Tipo de Mantenimiento"
        verbose_name_plural = "Tipos de Mantenimiento"
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    def es_aplicable_a_vehiculo(self, vehiculo):
        """Verifica si este tipo de mantenimiento es aplicable al vehículo dado"""
        return (self.vehiculos_aplicables == 'todos' or 
                self.vehiculos_aplicables == vehiculo.tipo)


class IntervaloMantenimiento(models.Model):
    """Modelo para personalizar intervalos de mantenimiento por vehículo"""
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        verbose_name="Vehículo",
        related_name="intervalos_personalizados"
    )
    
    tipo_mantenimiento = models.ForeignKey(
        TipoMantenimiento,
        on_delete=models.CASCADE,
        verbose_name="Tipo de mantenimiento"
    )
    
    intervalo_km_personalizado = models.PositiveIntegerField(
        verbose_name="Intervalo en kilómetros (personalizado)",
        help_text="Intervalo específico para este vehículo (0 = usar valor por defecto)",
        default=0,
        blank=True
    )
    
    intervalo_meses_personalizado = models.PositiveIntegerField(
        verbose_name="Intervalo en meses (personalizado)",
        help_text="Intervalo específico para este vehículo (0 = usar valor por defecto)",
        default=0,
        blank=True
    )
    
    notas = models.TextField(
        verbose_name="Notas",
        help_text="Razón de la personalización (ej: 'Motor turbo requiere cambios más frecuentes')",
        blank=True
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    class Meta:
        verbose_name = "Intervalo de Mantenimiento Personalizado"
        verbose_name_plural = "Intervalos de Mantenimiento Personalizados"
        unique_together = ['vehiculo', 'tipo_mantenimiento']
        ordering = ['vehiculo', 'tipo_mantenimiento']
    
    def __str__(self):
        return f"{self.vehiculo} - {self.tipo_mantenimiento.nombre}"
    
    def get_intervalo_km(self):
        """Devuelve el intervalo en km (personalizado o por defecto)"""
        return self.intervalo_km_personalizado or self.tipo_mantenimiento.intervalo_km
    
    def get_intervalo_meses(self):
        """Devuelve el intervalo en meses (personalizado o por defecto)"""
        return self.intervalo_meses_personalizado or self.tipo_mantenimiento.intervalo_meses
    
    def es_personalizado(self):
        """Indica si tiene intervalos personalizados"""
        return (self.intervalo_km_personalizado > 0 or 
                self.intervalo_meses_personalizado > 0)


class RegistroMantenimiento(models.Model):
    """Modelo para registrar una sesión de mantenimiento en el taller"""
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        verbose_name="Vehículo",
        related_name="mantenimientos"
    )
    
    fecha_realizacion = models.DateField(
        verbose_name="Fecha de realización",
        help_text="Fecha en que se realizó el mantenimiento"
    )
    
    kilometraje_realizacion = models.PositiveIntegerField(
        verbose_name="Kilometraje de realización",
        help_text="Kilómetros del vehículo cuando se realizó el mantenimiento"
    )
    
    costo_mano_obra_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo total de mano de obra",
        help_text="Costo total del trabajo realizado en euros",
        null=True,
        blank=True
    )
    
    taller = models.CharField(
        max_length=100,
        verbose_name="Taller/Lugar",
        help_text="Dónde se realizó el mantenimiento",
        blank=True
    )
    
    notas_generales = models.TextField(
        verbose_name="Notas generales",
        help_text="Observaciones adicionales sobre toda la sesión de mantenimiento",
        blank=True
    )
    
    iva_incluido = models.BooleanField(
        default=True,
        verbose_name="IVA incluido (21%)",
        help_text="Marcar si los precios ya incluyen IVA. Si no está marcado, se añadirá 21% al total"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    class Meta:
        verbose_name = "Registro de Mantenimiento"
        verbose_name_plural = "Registros de Mantenimiento"
        ordering = ['-fecha_realizacion']
    
    def __str__(self):
        items_count = self.items.count()
        if items_count == 1:
            return f"{self.vehiculo} - {self.items.first().tipo_mantenimiento.nombre} ({self.fecha_realizacion})"
        elif items_count > 1:
            return f"{self.vehiculo} - Mantenimiento múltiple ({items_count} trabajos) ({self.fecha_realizacion})"
        else:
            return f"{self.vehiculo} - Mantenimiento ({self.fecha_realizacion})"
    
    @property
    def costo_materiales_total(self):
        """Calcula el costo total de todos los materiales/piezas"""
        total = sum(item.costo_total for item in self.items.all())
        return Decimal(str(total)) if total else Decimal('0.00')
    
    @property
    def costo_subtotal(self):
        """Calcula el subtotal (materiales + mano de obra) sin IVA"""
        materiales = self.costo_materiales_total
        mano_obra = self.costo_mano_obra_total or Decimal('0.00')
        return materiales + mano_obra
    
    @property
    def costo_iva(self):
        """Calcula el importe del IVA (21%)"""
        if self.iva_incluido:
            return Decimal('0.00')
        return self.costo_subtotal * Decimal('0.21')
    
    @property
    def costo_total(self):
        """Calcula el costo total final (con o sin IVA según corresponda)"""
        if self.iva_incluido:
            return self.costo_subtotal
        return self.costo_subtotal + self.costo_iva
    
    def get_desglose_costos(self):
        """Retorna un diccionario con el desglose detallado de costos"""
        return {
            'materiales': self.costo_materiales_total,
            'mano_obra': self.costo_mano_obra_total or Decimal('0.00'),
            'subtotal': self.costo_subtotal,
            'iva_incluido': self.iva_incluido,
            'iva_importe': self.costo_iva,
            'total': self.costo_total,
            'items': [
                {
                    'descripcion': item.descripcion,
                    'cantidad': item.cantidad,
                    'costo_unitario': item.costo_unitario,
                    'costo_total': item.costo_total
                }
                for item in self.items.all()
            ]
        }
    
    def get_tipos_mantenimiento(self):
        """Retorna una lista de tipos de mantenimiento realizados"""
        return list(set(item.tipo_mantenimiento for item in self.items.all()))
    
    def get_proximos_mantenimientos(self):
        """Obtiene información sobre próximos mantenimientos basados en los items realizados"""
        proximos = []
        for item in self.items.all():
            try:
                intervalo_personalizado = IntervaloMantenimiento.objects.get(
                    vehiculo=self.vehiculo,
                    tipo_mantenimiento=item.tipo_mantenimiento
                )
                intervalo_km = intervalo_personalizado.get_intervalo_km()
                intervalo_meses = intervalo_personalizado.get_intervalo_meses()
            except IntervaloMantenimiento.DoesNotExist:
                intervalo_km = item.tipo_mantenimiento.intervalo_km
                intervalo_meses = item.tipo_mantenimiento.intervalo_meses
            
            proximo_info = {
                'tipo': item.tipo_mantenimiento,
                'ultimo_km': self.kilometraje_realizacion,
                'proximo_km': self.kilometraje_realizacion + intervalo_km if intervalo_km > 0 else None,
                'proximo_fecha': None
            }
            
            if intervalo_meses > 0:
                from dateutil.relativedelta import relativedelta
                proximo_info['proximo_fecha'] = self.fecha_realizacion + relativedelta(months=intervalo_meses)
            
            proximos.append(proximo_info)
        
        return proximos


class ItemMantenimiento(models.Model):
    """Modelo para cada trabajo/pieza específica dentro de una sesión de mantenimiento"""
    
    registro = models.ForeignKey(
        RegistroMantenimiento,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Registro de mantenimiento"
    )
    
    tipo_mantenimiento = models.ForeignKey(
        TipoMantenimiento,
        on_delete=models.CASCADE,
        verbose_name="Tipo de trabajo"
    )
    
    descripcion = models.CharField(
        max_length=200,
        verbose_name="Descripción del ítem",
        help_text="Ej: Filtro de aceite Mann W712, Aceite 5W30 Castrol, etc.",
        blank=True
    )
    
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad",
        help_text="Cantidad de unidades utilizadas"
    )
    
    costo_unitario = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Costo unitario",
        help_text="Costo por unidad en euros"
    )
    
    class Meta:
        verbose_name = "Ítem de Mantenimiento"
        verbose_name_plural = "Ítems de Mantenimiento"
        ordering = ['tipo_mantenimiento__nombre']
    
    def __str__(self):
        return f"{self.descripcion} ({self.cantidad}x {self.costo_unitario}€)"
    
    @property
    def costo_total(self):
        """Calcula el costo total del ítem (cantidad × precio unitario)"""
        return self.cantidad * self.costo_unitario


class UserRegistrationRequest(models.Model):
    """Modelo para almacenar solicitudes de registro de usuarios pendientes de aprobación"""
    
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    REGISTRATION_TYPE_CHOICES = [
        ('manual', 'Registro Manual'),
        ('google', 'Registro con Google'),
    ]
    
    username = models.CharField(
        max_length=150,
        verbose_name="Nombre de usuario",
        help_text="Nombre de usuario único para el nuevo usuario"
    )
    email = models.EmailField(
        verbose_name="Correo electrónico",
        help_text="Dirección de correo electrónico del solicitante"
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name="Nombre",
        help_text="Nombre del solicitante"
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Apellidos",
        help_text="Apellidos del solicitante"
    )
    password_hash = models.CharField(
        max_length=128,
        verbose_name="Hash de contraseña",
        help_text="Hash de la contraseña del usuario",
        null=True,
        blank=True  # Para cuentas de Google no necesitamos password
    )
    
    # Nuevos campos para manejar cuentas sociales
    registration_type = models.CharField(
        max_length=20,
        choices=REGISTRATION_TYPE_CHOICES,
        default='manual',
        verbose_name="Tipo de registro",
        help_text="Método usado para el registro"
    )
    google_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Google ID",
        help_text="ID único de Google del usuario"
    )
    google_picture = models.URLField(
        null=True,
        blank=True,
        verbose_name="Foto de Google",
        help_text="URL de la foto de perfil de Google"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendiente',
        verbose_name="Estado",
        help_text="Estado actual de la solicitud"
    )
    
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de solicitud",
        help_text="Fecha y hora de la solicitud"
    )
    fecha_procesado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de procesado",
        help_text="Fecha y hora de aprobación/rechazo"
    )
    procesado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Procesado por",
        help_text="Usuario administrador que procesó la solicitud"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas adicionales del administrador"
    )
    
    class Meta:
        verbose_name = "Solicitud de Registro"
        verbose_name_plural = "Solicitudes de Registro"
        ordering = ['-fecha_solicitud']
        app_label = 'auth'
        default_related_name = 'registration_requests'
    
    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name}) - {self.get_status_display()}"
    
    def aprobar(self, admin_user, notas=""):
        """Aprobar la solicitud y crear el usuario"""
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password
        from django.utils import timezone
        
        if self.status != 'pendiente':
            raise ValueError("Solo se pueden aprobar solicitudes pendientes")
        
        # Verificar que el username no exista
        if User.objects.filter(username=self.username).exists():
            raise ValueError("El nombre de usuario ya existe")
        
        # Crear el usuario con configuración según el tipo de registro
        if self.registration_type == 'google':
            # Para cuentas de Google, generar password aleatoria (no se usará)
            import secrets
            random_password = secrets.token_urlsafe(32)
            user = User.objects.create(
                username=self.username,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                password=make_password(random_password),
                is_active=True
            )
            
            # Crear la cuenta social vinculada
            self._crear_cuenta_social(user)
        else:
            # Para cuentas manuales, usar la password proporcionada
            user = User.objects.create(
                username=self.username,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                password=self.password_hash,  # Ya viene hasheada
                is_active=True
            )
        
        # Actualizar la solicitud
        self.status = 'aprobado'
        self.fecha_procesado = timezone.now()
        self.procesado_por = admin_user
        self.notas = notas
        self.save()
        
        # Enviar email de notificación al usuario aprobado
        self._enviar_email_aprobacion()
        
        return user
    
    def _crear_cuenta_social(self, user):
        """Crear la cuenta social vinculada para usuarios de Google"""
        if self.registration_type == 'google' and self.google_id:
            from allauth.socialaccount.models import SocialAccount, SocialApp
            
            try:
                # Buscar la aplicación social de Google
                google_app = SocialApp.objects.get(provider='google')
                
                # Crear la cuenta social
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider='google',
                    uid=self.google_id,
                    extra_data={
                        'picture': self.google_picture,
                        'name': f"{self.first_name} {self.last_name}",
                        'email': self.email,
                    }
                )
                social_account.save()
                
            except SocialApp.DoesNotExist:
                # Si no existe la app de Google configurada, continuar sin crear la cuenta social
                pass
    
    def rechazar(self, admin_user, notas=""):
        """Rechazar la solicitud"""
        from django.utils import timezone
        
        if self.status != 'pendiente':
            raise ValueError("Solo se pueden rechazar solicitudes pendientes")
        
        self.status = 'rechazado'
        self.fecha_procesado = timezone.now()
        self.procesado_por = admin_user
        self.notas = notas
        self.save()
        
        # Enviar email de notificación al usuario rechazado
        self._enviar_email_rechazo(notas)

    def _get_login_url(self):
        """Obtener URL de login con el dominio principal correcto"""
        from django.conf import settings
        import re
        
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        domain = 'localhost:8200'  # fallback
        
        # Buscar primero dominios reales (que contienen letras, no solo IP)
        for host in allowed_hosts:
            if host not in ['*', 'localhost', '127.0.0.1', '0.0.0.0']:
                # Verificar que no sea una IP (contiene letras, no solo números y puntos)
                if re.search(r'[a-zA-Z]', host):
                    domain = host
                    break
        
        # Si no encontramos dominio con letras, usar cualquier host que no esté excluido
        if domain == 'localhost:8200':
            for host in allowed_hosts:
                if host not in ['*', 'localhost', '127.0.0.1', '0.0.0.0']:
                    domain = host
                    break
        
        # Construir URL completa
        protocol = "https" if domain != 'localhost:8200' else "http"
        return f"{protocol}://{domain}{settings.LOGIN_URL}"

    def _enviar_email_aprobacion(self):
        """Enviar email de notificación cuando se aprueba la solicitud"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Obtener URL de login con dominio correcto
            login_url = self._get_login_url()
            
            # Mensaje diferente según el tipo de registro
            if self.registration_type == 'google':
                credenciales_info = "Ya puedes acceder al sistema usando tu cuenta de Google (botón 'Iniciar sesión con Google')."
            else:
                credenciales_info = f"""Ya puedes acceder al sistema con tus credenciales:
- Nombre de usuario: {self.username}
- Contraseña: La que proporcionaste al registrarte"""
            
            subject = '[Wheeler Keeper] ¡Tu solicitud ha sido aprobada!'
            message = f"""
Hola {self.first_name},

¡Excelentes noticias! Tu solicitud de registro en Wheeler Keeper ha sido aprobada.

{credenciales_info}

Accede al sistema:
🔗 Iniciar sesión: {login_url}

¡Bienvenido/a a Wheeler Keeper!

Saludos,
El equipo de Wheeler Keeper
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
                fail_silently=False,
            )
            logger.info(f"Email de aprobación enviado exitosamente a {self.email}")
            
        except Exception as e:
            # Log del error pero no fallar la aprobación
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando email de aprobación a {self.email}: {str(e)}")
            print(f"Error enviando email de aprobación a {self.email}: {str(e)}")

    def _enviar_email_rechazo(self, notas=""):
        """Enviar email de notificación cuando se rechaza la solicitud"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            import logging
            
            logger = logging.getLogger(__name__)
            
            subject = '[Wheeler Keeper] Solicitud de registro no aprobada'
            message = f"""
Hola {self.first_name},

Lamentamos informarte que tu solicitud de registro en Wheeler Keeper no ha sido aprobada en este momento.

Detalles de tu solicitud:
- Nombre de usuario solicitado: {self.username}
- Email: {self.email}
- Fecha de solicitud: {self.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}

{f"Motivo: {notas}" if notas else ""}

Si tienes preguntas sobre esta decisión, puedes contactar con el administrador.

Saludos,
El equipo de Wheeler Keeper
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
                fail_silently=False,
            )
            logger.info(f"Email de rechazo enviado exitosamente a {self.email}")
            
        except Exception as e:
            # Log del error pero no fallar el rechazo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando email de rechazo a {self.email}: {str(e)}")
            print(f"Error enviando email de rechazo a {self.email}: {str(e)}")


class NotificacionMantenimiento(models.Model):
    """Modelo para trackear notificaciones de mantenimiento enviadas"""
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        related_name="notificaciones_mantenimiento"
    )
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        verbose_name="Vehículo"
    )
    
    tipo_mantenimiento = models.ForeignKey(
        TipoMantenimiento,
        on_delete=models.CASCADE,
        verbose_name="Tipo de mantenimiento"
    )
    
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de envío"
    )
    
    tipo_alerta = models.CharField(
        max_length=20,
        choices=[
            ('proximo_km', 'Próximo por kilometraje'),
            ('proximo_tiempo', 'Próximo por tiempo'),
            ('vencido_km', 'Vencido por kilometraje'),
            ('vencido_tiempo', 'Vencido por tiempo'),
        ],
        verbose_name="Tipo de alerta"
    )
    
    kilometraje_notificado = models.PositiveIntegerField(
        verbose_name="Kilometraje cuando se notificó",
        help_text="Kilometraje del vehículo al momento de la notificación"
    )
    
    email_enviado = models.BooleanField(
        default=False,
        verbose_name="Email enviado"
    )
    
    class Meta:
        verbose_name = "Notificación de Mantenimiento"
        verbose_name_plural = "Notificaciones de Mantenimiento"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.vehiculo} - {self.tipo_mantenimiento.nombre} ({self.get_tipo_alerta_display()})"
    
    @classmethod
    def debe_notificar(cls, usuario, vehiculo, tipo_mantenimiento, tipo_alerta):
        """Verifica si se debe enviar una notificación (evita spam)"""
        from datetime import timedelta
        from django.utils import timezone
        
        # Verificar si ya se envió una notificación en las últimas 24 horas
        hace_24_horas = timezone.now() - timedelta(hours=24)
        
        existe_reciente = cls.objects.filter(
            usuario=usuario,
            vehiculo=vehiculo,
            tipo_mantenimiento=tipo_mantenimiento,
            tipo_alerta=tipo_alerta,
            fecha_envio__gte=hace_24_horas
        ).exists()
        
        return not existe_reciente
    
    @classmethod
    def registrar_notificacion(cls, usuario, vehiculo, tipo_mantenimiento, tipo_alerta, email_enviado=True):
        """Registra una notificación enviada"""
        return cls.objects.create(
            usuario=usuario,
            vehiculo=vehiculo,
            tipo_mantenimiento=tipo_mantenimiento,
            tipo_alerta=tipo_alerta,
            kilometraje_notificado=vehiculo.kilometraje_actual,
            email_enviado=email_enviado
        )
