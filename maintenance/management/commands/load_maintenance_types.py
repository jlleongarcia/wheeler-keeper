from django.core.management.base import BaseCommand
from maintenance.models import TipoMantenimiento


class Command(BaseCommand):
    help = 'Carga los tipos de mantenimiento predefinidos'

    def handle(self, *args, **options):
        tipos_mantenimiento = [
            # Motor
            {
                'nombre': 'Cambio de aceite motor',
                'descripcion': 'Cambio del aceite del motor y filtro de aceite',
                'categoria': 'Motor',
                'intervalo_km': 15000,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de bujías',
                'descripcion': 'Sustitución de bujías de encendido',
                'categoria': 'Motor',
                'intervalo_km': 30000,
                'intervalo_meses': 24,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de correa de distribución',
                'descripcion': 'Sustitución de correa de distribución y tensor',
                'categoria': 'Motor',
                'intervalo_km': 100000,
                'intervalo_meses': 60,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de arandela del cárter',
                'descripcion': 'Sustitución de arandela del cárter de aceite',
                'categoria': 'Motor',
                'intervalo_km': 15000,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de bomba de agua',
                'descripcion': 'Sustitución de bomba de agua',
                'categoria': 'Motor',
                'intervalo_km': 120000,
                'intervalo_meses': 60,
                'vehiculos_aplicables': 'todos'
            },
            
            # Transmisión
            {
                'nombre': 'Cambio de valvulina',
                'descripcion': 'Cambio del aceite de la transmisión/caja de cambios',
                'categoria': 'Transmision',
                'intervalo_km': 60000,
                'intervalo_meses': 48,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de embrague',
                'descripcion': 'Sustitución del kit de embrague completo',
                'categoria': 'Transmision',
                'intervalo_km': 120000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            
            # Frenos
            {
                'nombre': 'Cambio de pastillas de freno',
                'descripcion': 'Sustitución de pastillas de freno',
                'categoria': 'Frenos',
                'intervalo_km': 60000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de líquido de frenos',
                'descripcion': 'Cambio del líquido de frenos y sangrado del sistema',
                'categoria': 'Frenos',
                'intervalo_km': 0,
                'intervalo_meses': 24,
                'vehiculos_aplicables': 'todos'
            },
            
            # Neumáticos
            {
                'nombre': 'Cambio de neumáticos',
                'descripcion': 'Sustitución de neumáticos por desgaste',
                'categoria': 'Neumaticos',
                'intervalo_km': 50000,
                'intervalo_meses': 60,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Alineación y equilibrado',
                'descripcion': 'Alineación de ruedas y equilibrado de neumáticos',
                'categoria': 'Neumaticos',
                'intervalo_km': 20000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            
            # Filtros
            {
                'nombre': 'Cambio de filtro de combustible',
                'descripcion': 'Sustitución del filtro de combustible',
                'categoria': 'Filtros',
                'intervalo_km': 30000,
                'intervalo_meses': 24,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de filtro de aceite',
                'descripcion': 'Sustitución del filtro de aceite del motor',
                'categoria': 'Filtros',
                'intervalo_km': 15000,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de filtro de aire',
                'descripcion': 'Sustitución del filtro de aire del motor',
                'categoria': 'Filtros',
                'intervalo_km': 20000,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de filtro de polen',
                'descripcion': 'Sustitución del filtro de polen del habitáculo',
                'categoria': 'Filtros',
                'intervalo_km': 15000,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },
            
            # Suspensión
            {
                'nombre': 'Cambio de amortiguadores',
                'descripcion': 'Sustitución de amortiguadores delanteros o traseros',
                'categoria': 'Suspension',
                'intervalo_km': 80000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de guardapolvos de suspensión',
                'descripcion': 'Sustitución de guardapolvos de amortiguadores y rótulas',
                'categoria': 'Suspension',
                'intervalo_km': 60000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            
            # Sistema Eléctrico
            {
                'nombre': 'Cambio de batería',
                'descripcion': 'Sustitución de la batería del vehículo',
                'categoria': 'Electrico',
                'intervalo_km': 0,
                'intervalo_meses': 48,
                'vehiculos_aplicables': 'todos'
            },
            
            # Climatización
            {
                'nombre': 'Recarga aire acondicionado',
                'descripcion': 'Recarga del gas del sistema de aire acondicionado',
                'categoria': 'Climatizacion',
                'intervalo_km': 0,
                'intervalo_meses': 36,
                'vehiculos_aplicables': 'todos'
            },
            
            {
                'nombre': 'Cambio de guardapolvos de transmisión',
                'descripcion': 'Sustitución de guardapolvos de palieres y juntas homocinéticas',
                'categoria': 'Transmision',
                'intervalo_km': 80000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            
            # Específicos para motos
            {
                'nombre': 'Cambio de cadena y piñones',
                'descripcion': 'Sustitución de cadena de transmisión y piñones',
                'categoria': 'Transmision',
                'intervalo_km': 25000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'moto'
            },
            {
                'nombre': 'Ajuste de válvulas',
                'descripcion': 'Ajuste del juego de válvulas del motor',
                'categoria': 'Motor',
                'intervalo_km': 12000,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'moto'
            },

            # Otros líquidos
            {
                'nombre': 'Cambio de líquido refrigerante',
                'descripcion': 'Sustitución del líquido refrigerante del motor',
                'categoria': 'Motor',
                'intervalo_km': 60000,
                'intervalo_meses': 36,
                'vehiculos_aplicables': 'todos'
            },

            # Limpieza de lunas
            {
                'nombre': 'Cambio de líquido lavaparabrisas',
                'descripcion': 'Sustitución del líquido lavaparabrisas',
                'categoria': 'Lunas',
                'intervalo_km': 0,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Cambio de escobillas limpiaparabrisas',
                'descripcion': 'Sustitución de las escobillas del limpiaparabrisas',
                'categoria': 'Lunas',
                'intervalo_km': 0,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            },

            # Luces
            {
                'nombre': 'Cambio de bombillas',
                'descripcion': 'Sustitución de bombillas (general)',
                'categoria': 'Luces',
                'intervalo_km': 0,
                'intervalo_meses': 0,
                'vehiculos_aplicables': 'todos'
            },
            {
                'nombre': 'Pulimiento de faros',
                'descripcion': 'Pulimiento y restauración de faros delanteros',
                'categoria': 'Luces',
                'intervalo_km': 0,
                'intervalo_meses': 12,
                'vehiculos_aplicables': 'todos'
            }
        ]
        
        created_count = 0
        for tipo_data in tipos_mantenimiento:
            tipo, created = TipoMantenimiento.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults=tipo_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Creado: {tipo.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Ya existe: {tipo.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. {created_count} tipos de mantenimiento creados.'
            )
        )