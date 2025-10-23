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
]