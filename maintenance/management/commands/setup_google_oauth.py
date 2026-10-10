"""
Management command para configurar automáticamente Google OAuth
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from allauth.socialaccount.models import SocialApp

# allauth está montado en /oauth/ (ver wheeler_keeper/urls.py)
CALLBACK_URL = 'https://wheeler-keeper.box2overtake.com/oauth/google/login/callback/'


class Command(BaseCommand):
    help = 'Configura automáticamente Google OAuth para desarrollo'

    def handle(self, *args, **options):
        # Configurar el Site
        try:
            site = Site.objects.get(pk=1)
            site.domain = 'wheeler-keeper.box2overtake.com'
            site.name = 'Wheeler Keeper'
            site.save()
            self.stdout.write(
                self.style.SUCCESS(f'Site configurado: {site.domain}')
            )
        except Site.DoesNotExist:
            site = Site.objects.create(
                pk=1,
                domain='wheeler-keeper.box2overtake.com',
                name='Wheeler Keeper'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Site creado: {site.domain}')
            )

        # Crear o actualizar la aplicación social de Google
        # Las credenciales vienen de .env; si faltan, se usan valores temporales
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth Wheeler Keeper',
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID or 'temp_client_id_replace_with_real',
                'secret': settings.GOOGLE_OAUTH_CLIENT_SECRET or 'temp_secret_replace_with_real',
            }
        )
        
        # Asociar con el site
        google_app.sites.add(site)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✓ Aplicación social de Google creada con valores temporales')
            )
        else:
            self.stdout.write(
                self.style.WARNING('✓ Aplicación social de Google ya existía')
            )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('CONFIGURACIÓN COMPLETADA'))
        self.stdout.write('='*60)
        self.stdout.write('\n📋 PRÓXIMOS PASOS:')
        self.stdout.write('\n1. Obtén las credenciales de Google:')
        self.stdout.write('   - Ve a: https://console.cloud.google.com/')
        self.stdout.write('   - Crea/selecciona un proyecto')
        self.stdout.write('   - Configura la pantalla de consentimiento OAuth')
        self.stdout.write('   - Ve a Credenciales > Crear credenciales > ID de cliente OAuth 2.0 (Aplicación web)')
        self.stdout.write(f'   - URI de redirección autorizado: {CALLBACK_URL}')
        self.stdout.write('\n2. Añádelas a .env:')
        self.stdout.write('   - GOOGLE_OAUTH_CLIENT_ID=xxx-yyy.apps.googleusercontent.com')
        self.stdout.write('   - GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxx')
        self.stdout.write('\n3. Sincronízalas con la BD: python manage.py set_google_credentials')
        self.stdout.write('\n💡 MIENTRAS TANTO:')
        self.stdout.write('   - La aplicación funcionará normalmente')
        self.stdout.write('   - Los botones de Google estarán visibles')
        self.stdout.write('   - Solo fallarán cuando hagas clic (hasta que configures las credenciales reales)')
        self.stdout.write('='*60 + '\n')