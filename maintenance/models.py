from django.db import models
from django.contrib.auth.models import User


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
        return f"{self.marca} {self.modelo} ({self.get_tipo_display()})"
    
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
    """Modelo para registrar mantenimientos realizados"""
    
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        verbose_name="Vehículo",
        related_name="mantenimientos"
    )
    
    tipo_mantenimiento = models.ForeignKey(
        TipoMantenimiento,
        on_delete=models.CASCADE,
        verbose_name="Tipo de mantenimiento"
    )
    
    fecha_realizacion = models.DateField(
        verbose_name="Fecha de realización",
        help_text="Fecha en que se realizó el mantenimiento"
    )
    
    kilometraje_realizacion = models.PositiveIntegerField(
        verbose_name="Kilometraje de realización",
        help_text="Kilómetros del vehículo cuando se realizó el mantenimiento"
    )
    
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Costo",
        help_text="Costo del mantenimiento en euros",
        null=True,
        blank=True
    )
    
    taller = models.CharField(
        max_length=100,
        verbose_name="Taller/Lugar",
        help_text="Dónde se realizó el mantenimiento",
        blank=True
    )
    
    notas = models.TextField(
        verbose_name="Notas",
        help_text="Observaciones adicionales sobre el mantenimiento",
        blank=True
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
        return f"{self.vehiculo} - {self.tipo_mantenimiento.nombre} ({self.fecha_realizacion})"
    
    def get_intervalo_km(self):
        """Obtiene el intervalo en km (personalizado o por defecto)"""
        try:
            intervalo_personalizado = IntervaloMantenimiento.objects.get(
                vehiculo=self.vehiculo,
                tipo_mantenimiento=self.tipo_mantenimiento
            )
            return intervalo_personalizado.get_intervalo_km()
        except IntervaloMantenimiento.DoesNotExist:
            return self.tipo_mantenimiento.intervalo_km
    
    def get_intervalo_meses(self):
        """Obtiene el intervalo en meses (personalizado o por defecto)"""
        try:
            intervalo_personalizado = IntervaloMantenimiento.objects.get(
                vehiculo=self.vehiculo,
                tipo_mantenimiento=self.tipo_mantenimiento
            )
            return intervalo_personalizado.get_intervalo_meses()
        except IntervaloMantenimiento.DoesNotExist:
            return self.tipo_mantenimiento.intervalo_meses
    
    def proximo_por_km(self):
        """Calcula el próximo kilometraje para este mantenimiento"""
        intervalo_km = self.get_intervalo_km()
        if intervalo_km > 0:
            return self.kilometraje_realizacion + intervalo_km
        return None
    
    def proximo_por_fecha(self):
        """Calcula la próxima fecha para este mantenimiento"""
        intervalo_meses = self.get_intervalo_meses()
        if intervalo_meses > 0:
            from dateutil.relativedelta import relativedelta
            return self.fecha_realizacion + relativedelta(months=intervalo_meses)
        return None
    
    def es_vencimiento_proximo(self, margen_km=1000, margen_dias=30):
        """Determina si este mantenimiento está próximo a vencer"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Verificar vencimiento por kilómetros
        proximo_km = self.proximo_por_km()
        if proximo_km:
            km_actual = self.vehiculo.kilometraje_actual
            if km_actual >= (proximo_km - margen_km):
                return True, f"Próximo en {proximo_km - km_actual} km"
        
        # Verificar vencimiento por fecha
        proxima_fecha = self.proximo_por_fecha()
        if proxima_fecha:
            hoy = timezone.now().date()
            if hoy >= (proxima_fecha - timedelta(days=margen_dias)):
                dias_restantes = (proxima_fecha - hoy).days
                return True, f"Próximo en {dias_restantes} días"
        
        return False, "No próximo"


class UserRegistrationRequest(models.Model):
    """Modelo para almacenar solicitudes de registro de usuarios pendientes de aprobación"""
    
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
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
        help_text="Hash de la contraseña del usuario"
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
        
        # Crear el usuario
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

    def _enviar_email_aprobacion(self):
        """Enviar email de notificación cuando se aprueba la solicitud"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Obtener dominio principal configurado
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            domain = 'localhost:8200'  # fallback
            for host in allowed_hosts:
                if host not in ['*', 'localhost', '127.0.0.1', '0.0.0.0']:
                    domain = host
                    break
            
            login_url = f"https://{domain}{settings.LOGIN_URL}" if domain != 'localhost:8200' else f"http://{domain}{settings.LOGIN_URL}"
            
            subject = '[Wheeler Keeper] ¡Tu solicitud ha sido aprobada!'
            message = f"""
Hola {self.first_name},

¡Excelentes noticias! Tu solicitud de registro en Wheeler Keeper ha sido aprobada.

Ya puedes acceder al sistema con tus credenciales:
- Nombre de usuario: {self.username}
- Contraseña: La que proporcionaste al registrarte

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
            
        except Exception as e:
            # Log del error pero no fallar la aprobación
            print(f"Error enviando email de aprobación a {self.email}: {str(e)}")

    def _enviar_email_rechazo(self, notas=""):
        """Enviar email de notificación cuando se rechaza la solicitud"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
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
            
        except Exception as e:
            # Log del error pero no fallar el rechazo
            print(f"Error enviando email de rechazo a {self.email}: {str(e)}")
