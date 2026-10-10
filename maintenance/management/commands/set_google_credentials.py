"""
Comando para sincronizar las credenciales de Google OAuth desde .env a la BD (SocialApp)
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp

from .setup_google_oauth import CALLBACK_URL


class Command(BaseCommand):
    help = 'Sincroniza las credenciales de Google OAuth (.env por defecto) con la SocialApp de la BD'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Client ID de Google OAuth (por defecto: GOOGLE_OAUTH_CLIENT_ID de .env)',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Client Secret de Google OAuth (por defecto: GOOGLE_OAUTH_CLIENT_SECRET de .env)',
        )

    def handle(self, *args, **options):
        client_id = options.get('client_id') or settings.GOOGLE_OAUTH_CLIENT_ID
        client_secret = options.get('client_secret') or settings.GOOGLE_OAUTH_CLIENT_SECRET

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('❌ FALTAN CREDENCIALES')
            )
            self.stdout.write('\nDefine en .env:')
            self.stdout.write('GOOGLE_OAUTH_CLIENT_ID=xxx-yyy.apps.googleusercontent.com')
            self.stdout.write('GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxx')
            self.stdout.write('\nY ejecuta: python manage.py set_google_credentials')
            self.stdout.write('(o pásalas con --client-id y --client-secret)')
            self.stdout.write('\n📋 CÓMO OBTENER CREDENCIALES:')
            self.stdout.write('\n1. Ve a: https://console.cloud.google.com/')
            self.stdout.write('2. Crea/selecciona un proyecto')
            self.stdout.write('3. APIs y servicios > Pantalla de consentimiento OAuth (configúrala si no existe)')
            self.stdout.write('4. APIs y servicios > Credenciales > Crear credenciales > ID de cliente OAuth 2.0')
            self.stdout.write('5. Tipo: Aplicación web')
            self.stdout.write(f'6. URI de redirección autorizado: {CALLBACK_URL}')
            return

        try:
            # Actualizar la aplicación social existente
            google_app = SocialApp.objects.get(provider='google')
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()

            self.stdout.write(
                self.style.SUCCESS('✅ CREDENCIALES CONFIGURADAS EXITOSAMENTE')
            )
            self.stdout.write('\n' + '='*60)
            self.stdout.write('🎉 GOOGLE OAUTH LISTO')
            self.stdout.write('='*60)
            self.stdout.write('\n✅ Ahora puedes probar:')
            self.stdout.write('   - Ve a: https://wheeler-keeper.box2overtake.com/')
            self.stdout.write('   - Haz clic en "Iniciar sesión"')
            self.stdout.write('   - Haz clic en "Continuar con Google"')
            self.stdout.write('\n🔄 FLUJO COMPLETO:')
            self.stdout.write('   1. Usuario → "Registrarse con Google"')
            self.stdout.write('   2. Sistema → Crea solicitud pendiente')
            self.stdout.write('   3. Tú → Recibes email de notificación')
            self.stdout.write('   4. Tú → Apruebas desde admin')
            self.stdout.write('   5. Usuario → Puede hacer login con Google')
            self.stdout.write('='*60 + '\n')

        except SocialApp.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Error: No se encontró la aplicación social de Google')
            )
            self.stdout.write('\nEjecuta primero: python manage.py setup_google_oauth')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
