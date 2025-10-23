from django.contrib import admin
from .models import Vehiculo


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
