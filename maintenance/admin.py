from django.contrib import admin
from .models import Vehiculo, TipoMantenimiento, IntervaloMantenimiento, RegistroMantenimiento, UserRegistrationRequest


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    """Administración de vehículos en el panel de admin"""
    
    list_display = [
        'nombre_completo', 
        'tipo', 
        'propietario', 
        'matricula', 
        'kilometraje_actual', 
        'fecha_creacion'
    ]
    
    list_filter = [
        'tipo', 
        'marca', 
        'año', 
        'fecha_creacion'
    ]
    
    search_fields = [
        'marca', 
        'modelo', 
        'matricula', 
        'propietario__username'
    ]
    
    readonly_fields = [
        'fecha_creacion', 
        'fecha_actualizacion'
    ]
    
    fieldsets = (
        ('Información del Vehículo', {
            'fields': ('tipo', 'marca', 'modelo', 'año')
        }),
        ('Detalles', {
            'fields': ('propietario', 'matricula', 'kilometraje_actual')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('propietario')


@admin.register(TipoMantenimiento)
class TipoMantenimientoAdmin(admin.ModelAdmin):
    """Administración de tipos de mantenimiento"""
    
    list_display = [
        'nombre',
        'categoria', 
        'vehiculos_aplicables',
        'intervalo_km',
        'intervalo_meses',
        'activo'
    ]
    
    list_filter = [
        'categoria',
        'vehiculos_aplicables', 
        'activo'
    ]
    
    search_fields = [
        'nombre',
        'descripcion'
    ]
    
    list_editable = [
        'activo'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'activo')
        }),
        ('Intervalos de Mantenimiento', {
            'fields': ('intervalo_km', 'intervalo_meses'),
            'description': 'Especifica cada cuántos kilómetros y/o meses se debe realizar este mantenimiento. Usar 0 para indicar que no aplica.'
        }),
        ('Aplicabilidad', {
            'fields': ('vehiculos_aplicables',),
            'description': 'Selecciona a qué tipos de vehículos aplica este mantenimiento.'
        }),
    )


@admin.register(IntervaloMantenimiento)
class IntervaloMantenimientoAdmin(admin.ModelAdmin):
    """Administración de intervalos personalizados"""
    
    list_display = [
        'vehiculo',
        'tipo_mantenimiento',
        'intervalo_km_personalizado',
        'intervalo_meses_personalizado',
        'es_personalizado',
        'fecha_creacion'
    ]
    
    list_filter = [
        'tipo_mantenimiento__categoria',
        'vehiculo__tipo',
        'vehiculo__propietario'
    ]
    
    search_fields = [
        'vehiculo__marca',
        'vehiculo__modelo',
        'tipo_mantenimiento__nombre',
        'notas'
    ]
    
    fieldsets = (
        ('Vehículo y Mantenimiento', {
            'fields': ('vehiculo', 'tipo_mantenimiento')
        }),
        ('Intervalos Personalizados', {
            'fields': ('intervalo_km_personalizado', 'intervalo_meses_personalizado'),
            'description': 'Deja en 0 para usar los valores por defecto del tipo de mantenimiento.'
        }),
        ('Información Adicional', {
            'fields': ('notas',),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ['fecha_creacion']
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'vehiculo', 
            'tipo_mantenimiento',
            'vehiculo__propietario'
        )


@admin.register(RegistroMantenimiento)
class RegistroMantenimientoAdmin(admin.ModelAdmin):
    """Administración de registros de mantenimiento"""
    
    list_display = [
        'tipo_mantenimiento',
        'vehiculo',
        'fecha_realizacion',
        'kilometraje_realizacion',
        'costo_total',
        'taller'
    ]
    
    list_filter = [
        'tipo_mantenimiento__categoria',
        'fecha_realizacion',
        'vehiculo__tipo',
        'vehiculo__propietario'
    ]
    
    search_fields = [
        'tipo_mantenimiento__nombre',
        'vehiculo__marca',
        'vehiculo__modelo',
        'taller',
        'notas'
    ]
    
    date_hierarchy = 'fecha_realizacion'
    
    readonly_fields = [
        'fecha_creacion'
    ]
    
    fieldsets = (
        ('Mantenimiento', {
            'fields': ('vehiculo', 'tipo_mantenimiento')
        }),
        ('Detalles de Ejecución', {
            'fields': ('fecha_realizacion', 'kilometraje_realizacion', 'taller')
        }),
        ('Costos', {
            'fields': ('costo_materiales', 'costo_mano_obra'),
            'description': 'Especifica los costos de materiales y mano de obra por separado'
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('wide',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
        )

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related(
            'vehiculo', 
            'tipo_mantenimiento',
            'vehiculo__propietario'
        )
    
    def costo_total(self, obj):
        """Mostrar costo total formateado"""
        return f"${obj.costo_total:,.2f}"
    costo_total.short_description = "Costo Total"
    costo_total.admin_order_field = 'costo_materiales'


@admin.register(UserRegistrationRequest)
class UserRegistrationRequestAdmin(admin.ModelAdmin):
    """Administración de solicitudes de registro de usuarios"""
    
    list_display = [
        'username', 
        'first_name', 
        'last_name', 
        'email', 
        'status', 
        'fecha_solicitud',
        'procesado_por'
    ]
    
    list_filter = [
        'status', 
        'fecha_solicitud',
        'fecha_procesado'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name'
    ]
    
    readonly_fields = [
        'password_hash', 
        'fecha_solicitud', 
        'fecha_procesado'
    ]
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Estado', {
            'fields': ('status', 'notas')
        }),
        ('Información Técnica', {
            'fields': ('password_hash',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_procesado', 'procesado_por'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['aprobar_solicitudes', 'rechazar_solicitudes']
    
    def aprobar_solicitudes(self, request, queryset):
        """Acción para aprobar solicitudes seleccionadas"""
        aprobadas = 0
        errores = []
        
        for solicitud in queryset.filter(status='pendiente'):
            try:
                usuario = solicitud.aprobar(request.user, "Aprobado desde el panel de administración")
                aprobadas += 1
                self.message_user(
                    request, 
                    f"Usuario '{usuario.username}' creado exitosamente.",
                    level='success'
                )
            except ValueError as e:
                errores.append(f"Error con {solicitud.username}: {str(e)}")
        
        if aprobadas > 0:
            self.message_user(
                request,
                f"{aprobadas} solicitud(es) aprobada(s) exitosamente.",
                level='success'
            )
        
        for error in errores:
            self.message_user(request, error, level='error')
    
    aprobar_solicitudes.short_description = "Aprobar solicitudes seleccionadas"
    
    def rechazar_solicitudes(self, request, queryset):
        """Acción para rechazar solicitudes seleccionadas"""
        rechazadas = 0
        
        for solicitud in queryset.filter(status='pendiente'):
            try:
                solicitud.rechazar(request.user, "Rechazado desde el panel de administración")
                rechazadas += 1
            except ValueError as e:
                self.message_user(request, f"Error: {str(e)}", level='error')
        
        if rechazadas > 0:
            self.message_user(
                request,
                f"{rechazadas} solicitud(es) rechazada(s).",
                level='warning'
            )
    
    rechazar_solicitudes.short_description = "Rechazar solicitudes seleccionadas"
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('procesado_por')
    
    def has_add_permission(self, request):
        """No permitir agregar solicitudes desde el admin (solo desde formulario)"""
        return False