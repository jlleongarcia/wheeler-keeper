from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta

from maintenance.models import (
    Vehiculo, TipoMantenimiento, IntervaloMantenimiento, 
    RegistroMantenimiento, NotificacionMantenimiento
)


class Command(BaseCommand):
    help = 'Envía notificaciones por correo de mantenimientos próximos a vencer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Modo de prueba: muestra qué se enviaría pero no envía emails',
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Enviar solo al usuario con este email (para pruebas)',
        )
        parser.add_argument(
            '--usuario-id',
            type=int,
            help='Enviar solo al usuario con este ID (para middleware)',
        )
        parser.add_argument(
            '--silencioso',
            action='store_true',
            help='Modo silencioso: no mostrar output (para middleware)',
        )

    def handle(self, *args, **options):
        test_mode = options['test_mode']
        target_user_email = options.get('user_email')
        target_user_id = options.get('usuario_id')
        silencioso = options.get('silencioso', False)
        
        if not silencioso:
            self.stdout.write(self.style.SUCCESS('🚗 Iniciando verificación de mantenimientos próximos...'))
        
        # Filtrar usuarios
        if target_user_id:
            usuarios = User.objects.filter(id=target_user_id)
        elif target_user_email:
            usuarios = User.objects.filter(email=target_user_email)
            if not usuarios.exists():
                if not silencioso:
                    self.stdout.write(self.style.ERROR(f'No se encontró usuario con email: {target_user_email}'))
                return
        else:
            usuarios = User.objects.filter(email__isnull=False).exclude(email='')
        
        total_notificaciones = 0
        
        for usuario in usuarios:
            mantenimientos_proximos = self.obtener_mantenimientos_proximos(usuario)
            
            if mantenimientos_proximos:
                if test_mode:
                    if not silencioso:
                        self.stdout.write(f'📧 [MODO PRUEBA] Se enviaría email a {usuario.email}:')
                        for vehiculo, items in mantenimientos_proximos.items():
                            self.stdout.write(f'  🚙 {vehiculo}:')
                            for item in items:
                                self.stdout.write(f'    - {item["tipo_mantenimiento"].nombre}: {item["mensaje"]}')
                else:
                    self.enviar_notificacion(usuario, mantenimientos_proximos, silencioso)
                    total_notificaciones += 1
                    if not silencioso:
                        self.stdout.write(f'📧 Email enviado a {usuario.email}')
        
        if not silencioso:
            if test_mode:
                self.stdout.write(self.style.WARNING(f'🧪 Modo prueba completado. Se habrían enviado {len([u for u in usuarios if self.obtener_mantenimientos_proximos(u)])} notificaciones.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ Proceso completado. Se enviaron {total_notificaciones} notificaciones.'))

    def obtener_mantenimientos_proximos(self, usuario):
        """Obtiene todos los mantenimientos próximos a vencer para un usuario"""
        vehiculos = Vehiculo.objects.filter(propietario=usuario)
        mantenimientos_por_vehiculo = {}
        
        for vehiculo in vehiculos:
            mantenimientos_vehiculo = []
            
            # Obtener todos los tipos de mantenimiento aplicables
            tipos_aplicables = TipoMantenimiento.objects.filter(
                models.Q(vehiculos_aplicables='todos') | models.Q(vehiculos_aplicables=vehiculo.tipo),
                activo=True
            ).filter(
                models.Q(intervalo_km__gt=0) | models.Q(intervalo_meses__gt=0)
            )
            
            for tipo_mant in tipos_aplicables:
                # Buscar el último mantenimiento de este tipo
                ultimo_registro = RegistroMantenimiento.objects.filter(
                    vehiculo=vehiculo,
                    items__tipo_mantenimiento=tipo_mant
                ).order_by('-fecha_realizacion').first()
                
                if ultimo_registro:
                    # Buscar intervalo personalizado
                    intervalo_personalizado = IntervaloMantenimiento.objects.filter(
                        vehiculo=vehiculo,
                        tipo_mantenimiento=tipo_mant
                    ).first()
                    
                    # Determinar intervalos a usar
                    if intervalo_personalizado:
                        intervalo_km = intervalo_personalizado.intervalo_km_personalizado if intervalo_personalizado.intervalo_km_personalizado > 0 else tipo_mant.intervalo_km
                        intervalo_meses = intervalo_personalizado.intervalo_meses_personalizado if intervalo_personalizado.intervalo_meses_personalizado > 0 else tipo_mant.intervalo_meses
                    else:
                        intervalo_km = tipo_mant.intervalo_km or 0
                        intervalo_meses = tipo_mant.intervalo_meses or 0
                    
                    # Verificar si está próximo a vencer
                    es_proximo = False
                    mensaje = ""
                    urgencia = 0  # 0 = no urgente, 1 = próximo, 2 = vencido
                    
                    # Verificar por kilometraje
                    if intervalo_km > 0:
                        proximo_km = ultimo_registro.kilometraje_realizacion + intervalo_km
                        km_restantes = proximo_km - vehiculo.kilometraje_actual
                        
                        if km_restantes <= 1000:  # Próximo si faltan 1000 km o menos
                            es_proximo = True
                            if km_restantes <= 0:
                                mensaje = f"¡VENCIDO! (Pasado por {abs(km_restantes):.0f} km)"
                                urgencia = 2
                            else:
                                mensaje = f"Próximo en {km_restantes:.0f} km"
                                urgencia = 1
                    
                    # Verificar por fecha
                    if intervalo_meses > 0:
                        proxima_fecha = ultimo_registro.fecha_realizacion + relativedelta(months=intervalo_meses)
                        dias_restantes = (proxima_fecha - date.today()).days
                        
                        if dias_restantes <= 30:  # Próximo si faltan 30 días o menos
                            es_proximo = True
                            if dias_restantes <= 0:
                                if mensaje:
                                    mensaje += f" y ¡VENCIDO POR TIEMPO! (Pasado por {abs(dias_restantes)} días)"
                                else:
                                    mensaje = f"¡VENCIDO! (Pasado por {abs(dias_restantes)} días)"
                                urgencia = 2
                            else:
                                if mensaje:
                                    mensaje += f" o en {dias_restantes} días"
                                else:
                                    mensaje = f"Próximo en {dias_restantes} días"
                                if urgencia < 1:
                                    urgencia = 1
                    
                    if es_proximo:
                        # Determinar tipo de alerta
                        tipo_alerta = 'proximo_km'
                        if urgencia > 2:  # Vencido
                            if km_restantes <= 0:
                                tipo_alerta = 'vencido_km'
                            elif dias_restantes <= 0:
                                tipo_alerta = 'vencido_tiempo'
                        else:  # Próximo
                            if intervalo_meses > 0 and dias_restantes <= 30:
                                tipo_alerta = 'proximo_tiempo'
                        
                        # Verificar si ya se notificó hoy
                        if NotificacionMantenimiento.debe_notificar(
                            vehiculo.propietario, vehiculo, tipo_mant, tipo_alerta
                        ):
                            mantenimientos_vehiculo.append({
                                'tipo_mantenimiento': tipo_mant,
                                'ultimo_registro': ultimo_registro,
                                'mensaje': mensaje,
                                'urgencia': urgencia,
                                'proximo_km': proximo_km if intervalo_km > 0 else None,
                                'proxima_fecha': proxima_fecha if intervalo_meses > 0 else None,
                                'tipo_alerta': tipo_alerta,
                            })
            
            if mantenimientos_vehiculo:
                # Ordenar por urgencia (vencidos primero)
                mantenimientos_vehiculo.sort(key=lambda x: (-x['urgencia'], x['tipo_mantenimiento'].nombre))
                mantenimientos_por_vehiculo[vehiculo] = mantenimientos_vehiculo
        
        return mantenimientos_por_vehiculo

    def enviar_notificacion(self, usuario, mantenimientos_por_vehiculo, silencioso=False):
        """Envía el email de notificación al usuario"""
        
        # Contar total de mantenimientos
        total_mantenimientos = sum(len(items) for items in mantenimientos_por_vehiculo.values())
        total_vencidos = sum(
            len([item for item in items if item['urgencia'] == 2]) 
            for items in mantenimientos_por_vehiculo.values()
        )
        
        # Preparar contexto para el template
        contexto = {
            'usuario': usuario,
            'mantenimientos_por_vehiculo': mantenimientos_por_vehiculo,
            'total_mantenimientos': total_mantenimientos,
            'total_vencidos': total_vencidos,
            'fecha_hoy': date.today(),
        }
        
        # Renderizar el email
        html_message = render_to_string('maintenance/emails/notificacion_mantenimientos.html', contexto)
        plain_message = strip_tags(html_message)
        
        # Determinar asunto según urgencia
        if total_vencidos > 0:
            asunto = f'🚨 Wheeler Keeper - {total_vencidos} mantenimiento(s) vencido(s)'
        else:
            asunto = f'🔧 Wheeler Keeper - {total_mantenimientos} mantenimiento(s) próximo(s)'
        
        try:
            send_mail(
                subject=asunto,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            
            # Registrar las notificaciones enviadas
            self.registrar_notificaciones_enviadas(usuario, mantenimientos_por_vehiculo)
            
            return True
        except Exception as e:
            if not silencioso:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error enviando email a {usuario.email}: {str(e)}')
                )
            
            # Registrar como no enviadas en caso de error
            self.registrar_notificaciones_enviadas(usuario, mantenimientos_por_vehiculo, enviado=False)
            
            return False
    
    def registrar_notificaciones_enviadas(self, usuario, mantenimientos_por_vehiculo, enviado=True):
        """Registra en la base de datos las notificaciones que se enviaron"""
        for vehiculo, mantenimientos in mantenimientos_por_vehiculo.items():
            for item in mantenimientos:
                NotificacionMantenimiento.registrar_notificacion(
                    usuario=usuario,
                    vehiculo=vehiculo,
                    tipo_mantenimiento=item['tipo_mantenimiento'],
                    tipo_alerta=item['tipo_alerta'],
                    email_enviado=enviado
                )