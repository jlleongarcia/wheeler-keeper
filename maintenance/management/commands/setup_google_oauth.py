"""
Management command para configurar automáticamente Google OAuth
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


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
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth Wheeler Keeper',
                'client_id': 'temp_client_id_replace_with_real',
                'secret': 'temp_secret_replace_with_real',
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
        self.stdout.write('\n1. Ve al admin: http://wheeler-keeper.box2overtake.com/admin/')
        self.stdout.write('2. Ve a Social Applications > Google OAuth Wheeler Keeper')
        self.stdout.write('3. Reemplaza los valores temporales con:')
        self.stdout.write('   - Client ID: El que obtengas de Google Cloud Console')
        self.stdout.write('   - Secret key: El que obtengas de Google Cloud Console')
        self.stdout.write('\n4. Para obtener las credenciales de Google:')
        self.stdout.write('   - Ve a: https://console.cloud.google.com/')
        self.stdout.write('   - Crea/selecciona un proyecto')
        self.stdout.write('   - Habilita Google+ API')
        self.stdout.write('   - Ve a Credenciales > Crear credenciales > OAuth 2.0')
        self.stdout.write('   - URI de redirección: http://wheeler-keeper.box2overtake.com/accounts/google/login/callback/')
        self.stdout.write('\n💡 MIENTRAS TANTO:')
        self.stdout.write('   - La aplicación funcionará normalmente')
        self.stdout.write('   - Los botones de Google estarán visibles')
        self.stdout.write('   - Solo fallarán cuando hagas clic (hasta que configures las credenciales reales)')
        self.stdout.write('='*60 + '\n')