from django.utils.deprecation import MiddlewareMixin
from django.core.management import call_command
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NotificacionesMantenimientoMiddleware(MiddlewareMixin):
    """
    Middleware que verifica y envía notificaciones de mantenimiento
    de forma inteligente durante la navegación normal del usuario.
    """
    
    # Cache para evitar verificaciones muy frecuentes
    _ultima_verificacion = None
    _intervalo_verificacion = timedelta(hours=6)  # Verificar cada 6 horas máximo
    
    def process_request(self, request):
        """
        Procesa cada request y verifica si es momento de enviar notificaciones
        """
        # Solo ejecutar para usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Verificar si es momento de hacer la comprobación
        if not self._debe_verificar():
            return None
        
        # Verificar solo en requests GET normales (no AJAX, no archivos estáticos)
        if not self._es_request_apropiado(request):
            return None
        
        try:
            # Ejecutar comando de notificaciones en modo silencioso
            logger.info("Ejecutando verificación automática de notificaciones de mantenimiento")
            call_command(
                'enviar_notificaciones_mantenimiento',
                **{'silencioso': True, 'usuario_id': request.user.id}
            )
            
            # Actualizar tiempo de última verificación
            NotificacionesMantenimientoMiddleware._ultima_verificacion = datetime.now()
            
        except Exception as e:
            # Log del error pero no interrumpir la navegación del usuario
            logger.error(f"Error en verificación automática de notificaciones: {str(e)}")
        
        return None
    
    def _debe_verificar(self):
        """
        Determina si es momento de verificar notificaciones
        """
        if self._ultima_verificacion is None:
            return True
        
        tiempo_transcurrido = datetime.now() - self._ultima_verificacion
        return tiempo_transcurrido >= self._intervalo_verificacion
    
    def _es_request_apropiado(self, request):
        """
        Verifica si el request es apropiado para ejecutar verificaciones
        """
        # Solo requests GET
        if request.method != 'GET':
            return False
        
        # Evitar requests AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return False
        
        # Evitar archivos estáticos y API calls
        path = request.path
        excluded_paths = [
            '/static/',
            '/media/',
            '/admin/jsi18n/',
            '/favicon.ico'
        ]
        
        for excluded in excluded_paths:
            if path.startswith(excluded):
                return False
        
        return True


class NotificacionesProgramadasMiddleware(MiddlewareMixin):
    """
    Middleware alternativo que usa un enfoque más agresivo:
    verifica notificaciones una vez por día por usuario.
    """
    
    def process_request(self, request):
        """
        Verifica notificaciones una vez por día cuando el usuario se conecta
        """
        if not request.user.is_authenticated:
            return None
        
        # Solo en la página principal o dashboard
        if request.path not in ['/', '/inicio/', '/dashboard/']:
            return None
        
        # Verificar si ya se comprobó hoy para este usuario
        if self._ya_verificado_hoy(request.user):
            return None
        
        try:
            logger.info(f"Verificación diaria de notificaciones para usuario {request.user.username}")
            call_command(
                'enviar_notificaciones_mantenimiento',
                **{'silencioso': True, 'usuario_id': request.user.id}
            )
            
            # Marcar como verificado hoy
            self._marcar_verificado_hoy(request.user)
            
        except Exception as e:
            logger.error(f"Error en verificación diaria de notificaciones: {str(e)}")
        
        return None
    
    def _ya_verificado_hoy(self, usuario):
        """
        Verifica si ya se ejecutó la verificación hoy para este usuario
        """
        from django.core.cache import cache
        from datetime import date
        
        cache_key = f"notificaciones_verificadas_{usuario.id}_{date.today()}"
        return cache.get(cache_key, False)
    
    def _marcar_verificado_hoy(self, usuario):
        """
        Marca que ya se verificó hoy para este usuario
        """
        from django.core.cache import cache
        from datetime import date
        
        cache_key = f"notificaciones_verificadas_{usuario.id}_{date.today()}"
        # Expira a medianoche del día siguiente
        cache.set(cache_key, True, 86400)  # 24 horas