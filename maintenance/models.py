from django.db import models
from django.contrib.auth.models import User


class Vehiculo(models.Model):
    """Modelo para representar un vehículo del usuario"""
    
    TIPOS_VEHICULO = [
        ('moto', 'Moto'),
        ('coche', 'Coche'),
        ('furgoneta', 'Furgoneta'),
        ('autocaravana', 'Autocaravana'),
        ('camion', 'Camión'),
    ]
    
    propietario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Propietario",
        help_text="Usuario propietario del vehículo"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_VEHICULO,
        verbose_name="Tipo de vehículo",
        help_text="Selecciona el tipo de vehículo"
    )
    
    marca = models.CharField(
        max_length=50,
        verbose_name="Marca",
        help_text="Marca del vehículo (ej: BMW, Honda, Mercedes)"
    )
    
    modelo = models.CharField(
        max_length=100,
        verbose_name="Modelo",
        help_text="Modelo específico del vehículo"
    )
    
    año = models.PositiveIntegerField(
        verbose_name="Año de fabricación",
        help_text="Año de fabricación del vehículo",
        null=True,
        blank=True
    )
    
    matricula = models.CharField(
        max_length=20,
        verbose_name="Matrícula",
        help_text="Número de matrícula (opcional)",
        blank=True,
        null=True
    )
    
    kilometraje_actual = models.PositiveIntegerField(
        verbose_name="Kilometraje actual",
        help_text="Kilometraje actual del vehículo",
        default=0
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.get_tipo_display()})"
    
    def nombre_completo(self):
        """Devuelve el nombre completo del vehículo"""
        año_str = f" {self.año}" if self.año else ""
        return f"{self.marca} {self.modelo}{año_str}"
