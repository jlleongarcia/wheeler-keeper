from django.contrib import admin
from .models import Vehiculo, TipoMantenimiento, IntervaloMantenimiento, RegistroMantenimiento


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
        'costo',
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
            'fields': ('fecha_realizacion', 'kilometraje_realizacion', 'costo', 'taller')
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
