from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from datetime import timedelta
from .models import Vehiculo, TipoMantenimiento, IntervaloMantenimiento, RegistroMantenimiento
from .forms import VehiculoForm, RegistroMantenimientoForm, FiltroMantenimientoForm, UserRegistrationForm


@login_required
def inicio(request):
    """Página principal mostrando los vehículos del usuario y alertas de mantenimiento"""
    vehiculos = Vehiculo.objects.filter(propietario=request.user)
    
    # Obtener mantenimientos próximos a vencer
    mantenimientos_proximos = []
    for vehiculo in vehiculos:
        registros = RegistroMantenimiento.objects.filter(vehiculo=vehiculo)
        for registro in registros:
            es_proximo, mensaje = registro.es_vencimiento_proximo()
            if es_proximo:
                mantenimientos_proximos.append({
                    'registro': registro,
                    'mensaje': mensaje,
                    'vehiculo': vehiculo
                })
    
    # Obtener últimos mantenimientos
    ultimos_mantenimientos = RegistroMantenimiento.objects.filter(
        vehiculo__propietario=request.user
    ).select_related('vehiculo', 'tipo_mantenimiento')[:5]
    
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
    ).select_related('vehiculo', 'tipo_mantenimiento')
    
    if filtro_form.is_valid():
        vehiculo = filtro_form.cleaned_data.get('vehiculo')
        if vehiculo:
            mantenimientos = mantenimientos.filter(vehiculo=vehiculo)
        
        categoria = filtro_form.cleaned_data.get('categoria')
        if categoria:
            mantenimientos = mantenimientos.filter(tipo_mantenimiento__categoria=categoria)
        
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
    """Vista para agregar un nuevo registro de mantenimiento"""
    if request.method == 'POST':
        form = RegistroMantenimientoForm(request.POST, user=request.user)
        if form.is_valid():
            mantenimiento = form.save()
            messages.success(
                request, 
                f'Mantenimiento registrado: {mantenimiento.tipo_mantenimiento.nombre} para {mantenimiento.vehiculo}'
            )
            return redirect('maintenance:detalle_mantenimiento', mantenimiento_id=mantenimiento.id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroMantenimientoForm(user=request.user)
        
        # Si se pasa un vehículo por parámetro, preseleccionarlo
        vehiculo_id = request.GET.get('vehiculo')
        if vehiculo_id:
            try:
                vehiculo = Vehiculo.objects.get(id=vehiculo_id, propietario=request.user)
                form.fields['vehiculo'].initial = vehiculo
                # Filtrar tipos de mantenimiento para este vehículo
                tipos_aplicables = TipoMantenimiento.objects.filter(
                    Q(vehiculos_aplicables='todos') | Q(vehiculos_aplicables=vehiculo.tipo),
                    activo=True
                ).order_by('categoria', 'nombre')
                form.fields['tipo_mantenimiento'].queryset = tipos_aplicables
            except Vehiculo.DoesNotExist:
                pass
    
    return render(request, 'maintenance/mantenimientos/agregar.html', {
        'form': form
    })


@login_required
def detalle_mantenimiento(request, mantenimiento_id):
    """Vista para mostrar detalles de un mantenimiento"""
    mantenimiento = get_object_or_404(
        RegistroMantenimiento,
        id=mantenimiento_id,
        vehiculo__propietario=request.user
    )
    
    # Calcular próximo mantenimiento
    proximo_km = mantenimiento.proximo_por_km()
    proxima_fecha = mantenimiento.proximo_por_fecha()
    es_proximo, mensaje_alerta = mantenimiento.es_vencimiento_proximo()
    
    return render(request, 'maintenance/mantenimientos/detalle.html', {
        'mantenimiento': mantenimiento,
        'proximo_km': proximo_km,
        'proxima_fecha': proxima_fecha,
        'es_proximo': es_proximo,
        'mensaje_alerta': mensaje_alerta
    })


@login_required
def editar_mantenimiento(request, mantenimiento_id):
    """Vista para editar un mantenimiento existente"""
    mantenimiento = get_object_or_404(
        RegistroMantenimiento,
        id=mantenimiento_id,
        vehiculo__propietario=request.user
    )
    
    if request.method == 'POST':
        form = RegistroMantenimientoForm(request.POST, instance=mantenimiento, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de mantenimiento actualizado correctamente.')
            return redirect('maintenance:detalle_mantenimiento', mantenimiento_id=mantenimiento.id)
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroMantenimientoForm(instance=mantenimiento, user=request.user)
    
    return render(request, 'maintenance/mantenimientos/editar.html', {
        'form': form,
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
        nombre_mantenimiento = f"{mantenimiento.tipo_mantenimiento.nombre} - {mantenimiento.vehiculo}"
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
http://100.86.241.113:8200/admin/maintenance/userregistrationrequest/

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
