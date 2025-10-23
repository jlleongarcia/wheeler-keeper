from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Vehiculo
from .forms import VehiculoForm


@login_required
def inicio(request):
    """Página principal mostrando los vehículos del usuario"""
    vehiculos = Vehiculo.objects.filter(propietario=request.user)
    context = {
        'vehiculos': vehiculos,
        'total_vehiculos': vehiculos.count(),
    }
    return render(request, 'maintenance/inicio.html', context)


@login_required
def lista_vehiculos(request):
    """Vista para mostrar todos los vehículos del usuario"""
    vehiculos = Vehiculo.objects.filter(propietario=request.user)
    return render(request, 'maintenance/vehiculos/lista.html', {
        'vehiculos': vehiculos
    })


@login_required
def agregar_vehiculo(request):
    """Vista para agregar un nuevo vehículo"""
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.propietario = request.user
            vehiculo.save()
            messages.success(request, f'Vehículo {vehiculo.nombre_completo()} agregado correctamente.')
            return redirect('maintenance:lista_vehiculos')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = VehiculoForm()
    
    return render(request, 'maintenance/vehiculos/agregar.html', {
        'form': form
    })


@login_required
def detalle_vehiculo(request, vehiculo_id):
    """Vista para mostrar los detalles de un vehículo"""
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, propietario=request.user)
    return render(request, 'maintenance/vehiculos/detalle.html', {
        'vehiculo': vehiculo
    })


@login_required
def editar_vehiculo(request, vehiculo_id):
    """Vista para editar un vehículo existente"""
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, propietario=request.user)
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehículo {vehiculo.nombre_completo()} actualizado correctamente.')
            return redirect('maintenance:detalle_vehiculo', vehiculo_id=vehiculo.id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = VehiculoForm(instance=vehiculo)
    
    return render(request, 'maintenance/vehiculos/editar.html', {
        'form': form,
        'vehiculo': vehiculo
    })


@login_required
def eliminar_vehiculo(request, vehiculo_id):
    """Vista para eliminar un vehículo"""
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, propietario=request.user)
    
    if request.method == 'POST':
        nombre_vehiculo = vehiculo.nombre_completo()
        vehiculo.delete()
        messages.success(request, f'Vehículo {nombre_vehiculo} eliminado correctamente.')
        return redirect('maintenance:lista_vehiculos')
    
    return render(request, 'maintenance/vehiculos/eliminar.html', {
        'vehiculo': vehiculo
    })
