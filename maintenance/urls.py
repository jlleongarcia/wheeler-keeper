from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Página principal
    path('', views.inicio, name='inicio'),
    
    # Gestión de vehículos
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/agregar/', views.agregar_vehiculo, name='agregar_vehiculo'),
    path('vehiculos/<int:vehiculo_id>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('vehiculos/<int:vehiculo_id>/editar/', views.editar_vehiculo, name='editar_vehiculo'),
    path('vehiculos/<int:vehiculo_id>/eliminar/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    
    # Gestión de mantenimientos
    path('mantenimientos/', views.lista_mantenimientos, name='lista_mantenimientos'),
    path('mantenimientos/agregar/', views.agregar_mantenimiento, name='agregar_mantenimiento'),
    path('mantenimientos/<int:mantenimiento_id>/', views.detalle_mantenimiento, name='detalle_mantenimiento'),
    path('mantenimientos/<int:mantenimiento_id>/editar/', views.editar_mantenimiento, name='editar_mantenimiento'),
    path('mantenimientos/<int:mantenimiento_id>/eliminar/', views.eliminar_mantenimiento, name='eliminar_mantenimiento'),
    path('mantenimientos/proximos/', views.proximos_mantenimientos, name='proximos_mantenimientos'),
    
    # API endpoints
    path('api/tipos-mantenimiento/', views.get_tipos_mantenimiento_json, name='api_tipos_mantenimiento'),
]