from django import forms
from django.utils import timezone
from django.db import models
from .models import Vehiculo, TipoMantenimiento, RegistroMantenimiento


class VehiculoForm(forms.ModelForm):
    """Formulario para crear y editar vehículos"""
    
    class Meta:
        model = Vehiculo
        fields = [
            'tipo', 'marca', 'modelo', 'año', 
            'matricula', 'kilometraje_actual'
        ]
        widgets = {
            'tipo': forms.Select(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Selecciona el tipo de vehículo'
                }
            ),
            'marca': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: BMW, Honda, Mercedes...'
                }
            ),
            'modelo': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Civic, Serie 3, Sprinter...'
                }
            ),
            'año': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Año de fabricación',
                    'min': 1900,
                    'max': 2030
                }
            ),
            'matricula': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: 1234-ABC (opcional)'
                }
            ),
            'kilometraje_actual': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Kilometros actuales',
                    'min': 0
                }
            ),
        }
    
    def clean_año(self):
        """Validar que el año sea razonable"""
        año = self.cleaned_data.get('año')
        if año and (año < 1900 or año > 2030):
            raise forms.ValidationError('El año debe estar entre 1900 y 2030')
        return año
    
    def clean_marca(self):
        """Limpiar y capitalizar la marca"""
        marca = self.cleaned_data.get('marca')
        if marca:
            return marca.strip().title()
        return marca
    
    def clean_modelo(self):
        """Limpiar y capitalizar el modelo"""
        modelo = self.cleaned_data.get('modelo')
        if modelo:
            return modelo.strip().title()
        return modelo


class RegistroMantenimientoForm(forms.ModelForm):
    """Formulario para registrar un nuevo mantenimiento"""
    
    class Meta:
        model = RegistroMantenimiento
        fields = [
            'vehiculo', 'tipo_mantenimiento', 'fecha_realizacion', 
            'kilometraje_realizacion', 'costo', 'taller', 'notas'
        ]
        widgets = {
            'vehiculo': forms.Select(
                attrs={
                    'class': 'form-control',
                    'required': True
                }
            ),
            'tipo_mantenimiento': forms.Select(
                attrs={
                    'class': 'form-control',
                    'required': True
                }
            ),
            'fecha_realizacion': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'required': True
                }
            ),
            'kilometraje_realizacion': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Kilómetros cuando se realizó',
                    'min': 0,
                    'required': True
                }
            ),
            'costo': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00',
                    'min': 0,
                    'step': 0.01
                }
            ),
            'taller': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del taller o lugar'
                }
            ),
            'notas': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Observaciones, piezas cambiadas, etc.'
                }
            ),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar vehículos por usuario
        if user:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(
                propietario=user
            )
        
        # Si se está editando, filtrar tipos de mantenimiento por el vehículo
        if self.instance and self.instance.pk and self.instance.vehiculo:
            vehiculo = self.instance.vehiculo
            tipos_aplicables = TipoMantenimiento.objects.filter(
                models.Q(vehiculos_aplicables='todos') |
                models.Q(vehiculos_aplicables=vehiculo.tipo),
                activo=True
            )
            self.fields['tipo_mantenimiento'].queryset = tipos_aplicables
        
        # Establecer fecha por defecto como hoy
        if not self.instance.pk:
            self.fields['fecha_realizacion'].initial = timezone.now().date()
    
    def clean_fecha_realizacion(self):
        """Validar que la fecha no sea futura"""
        fecha = self.cleaned_data.get('fecha_realizacion')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError('La fecha de realización no puede ser futura')
        return fecha
    
    def clean_kilometraje_realizacion(self):
        """Validar que el kilometraje sea coherente"""
        kilometraje = self.cleaned_data.get('kilometraje_realizacion')
        vehiculo = self.cleaned_data.get('vehiculo')
        
        if kilometraje and vehiculo:
            # No puede ser mayor que el kilometraje actual
            if kilometraje > vehiculo.kilometraje_actual:
                raise forms.ValidationError(
                    f'El kilometraje no puede ser mayor al actual del vehículo ({vehiculo.kilometraje_actual} km)'
                )
        
        return kilometraje
    
    def clean(self):
        """Validación cruzada del formulario"""
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        tipo_mantenimiento = cleaned_data.get('tipo_mantenimiento')
        
        # Verificar que el tipo de mantenimiento sea aplicable al vehículo
        if vehiculo and tipo_mantenimiento:
            if not tipo_mantenimiento.es_aplicable_a_vehiculo(vehiculo):
                raise forms.ValidationError(
                    f'El mantenimiento "{tipo_mantenimiento.nombre}" no es aplicable a {vehiculo.get_tipo_display()}'
                )
        
        return cleaned_data


class FiltroMantenimientoForm(forms.Form):
    """Formulario para filtrar registros de mantenimiento"""
    
    vehiculo = forms.ModelChoiceField(
        queryset=Vehiculo.objects.none(),
        required=False,
        empty_label="Todos los vehículos",
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + TipoMantenimiento.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(
                propietario=user
            )