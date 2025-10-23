from django import forms
from .models import Vehiculo


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