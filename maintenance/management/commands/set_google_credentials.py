"""
Comando para configurar credenciales de Google OAuth para desarrollo
"""

from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Configura credenciales temporales de Google OAuth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Client ID de Google OAuth',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Client Secret de Google OAuth',
        )

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('❌ FALTAN CREDENCIALES')
            )
            self.stdout.write('\nUso:')
            self.stdout.write('python manage.py set_google_credentials --client-id="TU_CLIENT_ID" --client-secret="TU_CLIENT_SECRET"')
            self.stdout.write('\n📋 CÓMO OBTENER CREDENCIALES:')
            self.stdout.write('\n1. Ve a: https://console.cloud.google.com/')
            self.stdout.write('2. Crea/selecciona un proyecto')
            self.stdout.write('3. APIs y servicios > Credenciales')
            self.stdout.write('4. Crear credenciales > ID de cliente OAuth 2.0')
            self.stdout.write('5. Tipo: Aplicación web')
            self.stdout.write('6. URI de redirección: http://wheeler-keeper.box2overtake.com/accounts/google/login/callback/')
            self.stdout.write('\n🔗 FORMATO DE CREDENCIALES:')
            self.stdout.write('Client ID: xxx-yyy.apps.googleusercontent.com')
            self.stdout.write('Client Secret: GOCSPX-xxxxxxxxxx')
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
            self.stdout.write('   - Ve a: http://wheeler-keeper.box2overtake.com/')
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