from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from datetime import timedelta
from .models import Vehiculo, TipoMantenimiento, IntervaloMantenimiento, RegistroMantenimiento, ItemMantenimiento
from .forms import VehiculoForm, RegistroMantenimientoForm, ItemMantenimientoFormSet, FiltroMantenimientoForm, UserRegistrationForm


@login_required
def inicio(request):
    """Página principal mostrando los vehículos del usuario y alertas de mantenimiento"""
    vehiculos = Vehiculo.objects.filter(propietario=request.user)
    
    # TODO: Implementar lógica de mantenimientos próximos con nuevo modelo
    mantenimientos_proximos = []
    
    # Obtener últimos mantenimientos
    ultimos_mantenimientos = RegistroMantenimiento.objects.filter(
        vehiculo__propietario=request.user
    ).prefetch_related('items__tipo_mantenimiento')[:5]
    
    context = {
        'vehiculos': vehiculos,
        'total_vehiculos': vehiculos.count(),
        'mantenimientos_proximos': mantenimientos_proximos[:10],  # Máximo 10 alertas
        'ultimos_mantenimientos': ultimos_mantenimientos,
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
    
    # Obtener intervalos personalizados para este vehículo
    from .models import IntervaloMantenimiento
    intervalos_personalizados = IntervaloMantenimiento.objects.filter(
        vehiculo=vehiculo
    ).select_related('tipo_mantenimiento')
    
    # Obtener últimos mantenimientos
    ultimos_mantenimientos = vehiculo.mantenimientos.all()[:5]
    
    return render(request, 'maintenance/vehiculos/detalle.html', {
        'vehiculo': vehiculo,
        'intervalos_personalizados': intervalos_personalizados,
        'ultimos_mantenimientos': ultimos_mantenimientos
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


# ========== VISTAS DE MANTENIMIENTO ==========

@login_required
def lista_mantenimientos(request):
    """Vista para listar todos los mantenimientos del usuario"""
    # Aplicar filtros
    filtro_form = FiltroMantenimientoForm(request.GET, user=request.user)
    
    mantenimientos = RegistroMantenimiento.objects.filter(
        vehiculo__propietario=request.user
    ).select_related('vehiculo').prefetch_related('items__tipo_mantenimiento')
    
    if filtro_form.is_valid():
        vehiculo = filtro_form.cleaned_data.get('vehiculo')
        if vehiculo:
            mantenimientos = mantenimientos.filter(vehiculo=vehiculo)
        
        categoria = filtro_form.cleaned_data.get('categoria')
        if categoria:
            mantenimientos = mantenimientos.filter(items__tipo_mantenimiento__categoria=categoria).distinct()
        
        fecha_desde = filtro_form.cleaned_data.get('fecha_desde')
        if fecha_desde:
            mantenimientos = mantenimientos.filter(fecha_realizacion__gte=fecha_desde)
        
        fecha_hasta = filtro_form.cleaned_data.get('fecha_hasta')
        if fecha_hasta:
            mantenimientos = mantenimientos.filter(fecha_realizacion__lte=fecha_hasta)
    
    mantenimientos = mantenimientos.order_by('-fecha_realizacion')
    
    return render(request, 'maintenance/mantenimientos/lista.html', {
        'mantenimientos': mantenimientos,
        'filtro_form': filtro_form
    })


@login_required
def agregar_mantenimiento(request):
    """Vista para agregar un nuevo registro de mantenimiento con múltiples ítems"""
    if request.method == 'POST':
        form = RegistroMantenimientoForm(request.POST, user=request.user)
        formset = ItemMantenimientoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            mantenimiento = form.save()
            formset.instance = mantenimiento
            items = formset.save()
            
            # Crear mensaje de éxito con detalles
            items_nombres = [item.tipo_mantenimiento.nombre for item in items]
            if len(items_nombres) == 1:
                mensaje = f'Mantenimiento registrado: {items_nombres[0]} para {mantenimiento.vehiculo}'
            else:
                mensaje = f'Mantenimiento múltiple registrado ({len(items_nombres)} trabajos) para {mantenimiento.vehiculo}'
            
            messages.success(request, mensaje)
            return redirect('maintenance:detalle_mantenimiento', mantenimiento_id=mantenimiento.id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroMantenimientoForm(user=request.user)
        formset = ItemMantenimientoFormSet(queryset=ItemMantenimiento.objects.none())
        
        # Si se pasa un vehículo por parámetro, preseleccionarlo
        vehiculo_id = request.GET.get('vehiculo')
        if vehiculo_id:
            try:
                vehiculo = Vehiculo.objects.get(id=vehiculo_id, propietario=request.user)
                form.fields['vehiculo'].initial = vehiculo
            except Vehiculo.DoesNotExist:
                pass
    
    return render(request, 'maintenance/mantenimientos/agregar.html', {
        'form': form,
        'formset': formset
    })


@login_required
def detalle_mantenimiento(request, mantenimiento_id):
    """Vista para mostrar detalles de un mantenimiento"""
    mantenimiento = get_object_or_404(
        RegistroMantenimiento,
        id=mantenimiento_id,
        vehiculo__propietario=request.user
    )
    
    # Obtener ítems del mantenimiento
    items = mantenimiento.items.all().select_related('tipo_mantenimiento')
    
    # TODO: Implementar lógica de próximos mantenimientos
    proximos_mantenimientos = []  # mantenimiento.get_proximos_mantenimientos()
    
    return render(request, 'maintenance/mantenimientos/detalle.html', {
        'mantenimiento': mantenimiento,
        'items': items,
        'proximos_mantenimientos': proximos_mantenimientos,
    })


@login_required
def editar_mantenimiento(request, mantenimiento_id):
    """Vista para editar un mantenimiento existente con sus ítems"""
    mantenimiento = get_object_or_404(
        RegistroMantenimiento,
        id=mantenimiento_id,
        vehiculo__propietario=request.user
    )
    
    if request.method == 'POST':
        form = RegistroMantenimientoForm(request.POST, instance=mantenimiento, user=request.user)
        formset = ItemMantenimientoFormSet(request.POST, instance=mantenimiento)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Registro de mantenimiento actualizado correctamente.')
            return redirect('maintenance:detalle_mantenimiento', mantenimiento_id=mantenimiento.id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroMantenimientoForm(instance=mantenimiento, user=request.user)
        formset = ItemMantenimientoFormSet(instance=mantenimiento)
    
    return render(request, 'maintenance/mantenimientos/editar.html', {
        'form': form,
        'formset': formset,
        'mantenimiento': mantenimiento
    })


@login_required
def eliminar_mantenimiento(request, mantenimiento_id):
    """Vista para eliminar un mantenimiento"""
    mantenimiento = get_object_or_404(
        RegistroMantenimiento,
        id=mantenimiento_id,
        vehiculo__propietario=request.user
    )
    
    if request.method == 'POST':
        items_count = mantenimiento.items.count()
        if items_count == 1:
            nombre_mantenimiento = f"{mantenimiento.items.first().tipo_mantenimiento.nombre} - {mantenimiento.vehiculo}"
        else:
            nombre_mantenimiento = f"Mantenimiento múltiple ({items_count} trabajos) - {mantenimiento.vehiculo}"
        mantenimiento.delete()
        messages.success(request, f'Registro de mantenimiento "{nombre_mantenimiento}" eliminado correctamente.')
        return redirect('maintenance:lista_mantenimientos')
    
    return render(request, 'maintenance/mantenimientos/eliminar.html', {
        'mantenimiento': mantenimiento
    })


@login_required
def proximos_mantenimientos(request):
    """Vista para mostrar mantenimientos próximos a vencer"""
    vehiculos = Vehiculo.objects.filter(propietario=request.user)
    
    mantenimientos_proximos = []
    for vehiculo in vehiculos:
        registros = RegistroMantenimiento.objects.filter(vehiculo=vehiculo)
        for registro in registros:
            es_proximo, mensaje = registro.es_vencimiento_proximo()
            if es_proximo:
                proximo_km = registro.proximo_por_km()
                proxima_fecha = registro.proximo_por_fecha()
                mantenimientos_proximos.append({
                    'registro': registro,
                    'mensaje': mensaje,
                    'vehiculo': vehiculo,
                    'proximo_km': proximo_km,
                    'proxima_fecha': proxima_fecha
                })
    
    # Ordenar por prioridad (primero los más urgentes)
    mantenimientos_proximos.sort(key=lambda x: x['registro'].fecha_realizacion, reverse=True)
    
    return render(request, 'maintenance/mantenimientos/proximos.html', {
        'mantenimientos_proximos': mantenimientos_proximos
    })


@login_required
def get_tipos_mantenimiento_json(request):
    """API para obtener tipos de mantenimiento según el vehículo"""
    vehiculo_id = request.GET.get('vehiculo_id')
    if not vehiculo_id:
        return JsonResponse({'tipos': []})
    
    try:
        vehiculo = Vehiculo.objects.get(id=vehiculo_id, propietario=request.user)
        tipos = TipoMantenimiento.objects.filter(
            Q(vehiculos_aplicables='todos') | Q(vehiculos_aplicables=vehiculo.tipo),
            activo=True
        ).order_by('categoria', 'nombre')
        
        # Agrupar por categorías
        tipos_agrupados = {}
        categoria_labels = dict(TipoMantenimiento.CATEGORIA_CHOICES)
        
        for tipo in tipos:
            categoria = tipo.categoria
            if categoria not in tipos_agrupados:
                tipos_agrupados[categoria] = {
                    'label': categoria_labels.get(categoria, categoria.title()),
                    'tipos': []
                }
            
            tipos_agrupados[categoria]['tipos'].append({
                'id': tipo.id,
                'nombre': tipo.nombre,
                'intervalo_km': tipo.intervalo_km,
                'intervalo_meses': tipo.intervalo_meses
            })
        
        return JsonResponse({'categorias': tipos_agrupados})
    
    except Vehiculo.DoesNotExist:
        return JsonResponse({'tipos': []})


def registro_usuario(request):
    """Vista para el registro de nuevos usuarios (requiere aprobación)"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Guardar la solicitud de registro
            solicitud = form.save()
            
            # Enviar email de notificación al administrador
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                from django.contrib.auth.models import User
                
                # Obtener email del usuario sa (administrador)
                try:
                    admin_user = User.objects.get(username='sa')
                    admin_email = admin_user.email
                    # Si el usuario sa no tiene email configurado, usar el de configuración
                    if not admin_email:
                        admin_email = settings.ADMIN_EMAIL
                except User.DoesNotExist:
                    # Si no existe usuario sa, usar email de configuración
                    admin_email = settings.ADMIN_EMAIL
                
                subject = f'[Wheeler Keeper] Nueva solicitud de registro - {solicitud.username}'
                message = f"""
Hola Administrador,

Se ha recibido una nueva solicitud de registro en Wheeler Keeper.

Detalles del solicitante:
- Nombre de usuario: {solicitud.username}
- Nombre completo: {solicitud.first_name} {solicitud.last_name}
- Email: {solicitud.email}
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
                
            except Exception as e:
                # Si falla el envío del email, log del error pero continúa
                print(f"Error enviando email de notificación: {e}")
            
            messages.success(
                request, 
                f'¡Solicitud de registro enviada exitosamente! Tu solicitud está pendiente de aprobación por el administrador. Te contactaremos a {solicitud.email} cuando sea procesada.'
            )
            return redirect('maintenance:registro_exitoso')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/registro.html', {'form': form})


def registro_exitoso(request):
    """Vista para mostrar mensaje de éxito tras el registro"""
    return render(request, 'registration/registro_exitoso.html')
