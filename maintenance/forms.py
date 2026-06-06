from django import forms
from django.utils import timezone
from django.db import models
from django.utils.safestring import mark_safe
from itertools import groupby
from .models import Vehiculo, TipoMantenimiento, RegistroMantenimiento, ItemMantenimiento


def tipo_mantenimiento_categoria_choices(vehiculo=None, user=None, include_empty=True):
    """Return tipos de mantenimiento grouped by categoria, suitable for using as optgroups for select inputs"""

    def categoria_display(t):
        return "%s" % (t.get_categoria_display())

    def tipo_name(t):
        return "%s" % (t.nombre)

    tipos = TipoMantenimiento.visibles_para_usuario(user=user, vehiculo=vehiculo).order_by("categoria", "nombre")

    choices = [(categoria, list(tipos_cat)) for (categoria, tipos_cat) in groupby(tipos, key=categoria_display)]
    choices = [(categoria, [(t.id, tipo_name(t)) for t in tipos_cat]) for (categoria, tipos_cat) in choices]
    
    if include_empty:
        choices = [("", "---------")] + choices

    return choices


class TipoMantenimientoModelChoiceField(forms.ModelChoiceField):
    """Campo personalizado para mostrar tipos de mantenimiento agrupados por categoría"""
    
    def __init__(self, vehiculo=None, user=None, *args, **kwargs):
        self.vehiculo = vehiculo
        self.user = user
        # Configurar queryset base - usar none() para evitar consultas en import
        try:
            queryset = TipoMantenimiento.visibles_para_usuario(user=user, vehiculo=vehiculo)
        except Exception:
            # Si hay error de DB (como en primera instalación), usar queryset vacío
            queryset = TipoMantenimiento.objects.none()
        
        kwargs['queryset'] = queryset
        super().__init__(*args, **kwargs)
        # No llamar update_choices en __init__ para evitar consultas durante import
        self._choices_updated = False
    
    def update_choices(self):
        """Actualiza las opciones con agrupación por categorías"""
        try:
            self.choices = tipo_mantenimiento_categoria_choices(
                vehiculo=self.vehiculo,
                user=self.user,
                include_empty=True
            )
            self._choices_updated = True
        except Exception:
            # Si hay error de DB, usar choices vacías
            self.choices = [("", "---------")]
            self._choices_updated = False
    
    @property
    def choices(self):
        """Lazy loading de choices"""
        if not getattr(self, '_choices_updated', False):
            self.update_choices()
        return super().choices
    
    @choices.setter
    def choices(self, value):
        """Setter para choices"""
        super(TipoMantenimientoModelChoiceField, self.__class__).choices.fset(self, value)
    
    def set_vehiculo(self, vehiculo):
        """Actualiza el vehículo y regenera las opciones"""
        self.vehiculo = vehiculo
        # Actualizar queryset
        queryset = TipoMantenimiento.visibles_para_usuario(user=self.user, vehiculo=vehiculo)
        self.queryset = queryset
        self.update_choices()

    def set_user(self, user):
        """Actualiza el usuario y regenera las opciones visibles."""
        self.user = user
        self.queryset = TipoMantenimiento.visibles_para_usuario(user=user, vehiculo=self.vehiculo)
        self.update_choices()


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
    """Formulario para registrar una sesión de mantenimiento"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar vehículos por propietario
        if self.user:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(propietario=self.user)
        
        # Establecer fecha por defecto como hoy
        if not self.instance.pk:
            self.fields['fecha_realizacion'].initial = timezone.now().date()
    
    class Meta:
        model = RegistroMantenimiento
        fields = [
            'vehiculo', 'fecha_realizacion', 'kilometraje_realizacion', 
            'costo_mano_obra_total', 'taller', 'iva_incluido', 'notas_generales'
        ]
        widgets = {
            'vehiculo': forms.Select(
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
            'costo_mano_obra_total': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00 (costo total de mano de obra)',
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
            'iva_incluido': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'id': 'id_iva_incluido'
                }
            ),
            'notas_generales': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Observaciones generales sobre la sesión de mantenimiento'
                }
            ),
        }

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

        # Only validate km for new records; when editing historical records the
        # vehicle's current km may already have been updated past the record km.
        if kilometraje and vehiculo and not self.instance.pk:
            if kilometraje > vehiculo.kilometraje_actual:
                raise forms.ValidationError(
                    f'El kilometraje no puede ser mayor al actual del vehículo ({vehiculo.kilometraje_actual} km)'
                )

        return kilometraje
    
    def clean(self):
        """Validación cruzada del formulario"""
        cleaned_data = super().clean()
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


class UserRegistrationForm(forms.Form):
    """Formulario para solicitudes de registro de usuarios"""
    
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        help_text="Requerido. 150 caracteres o menos. Únicamente letras, dígitos y @/./+/-/_ permitidos.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario'
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        help_text="Ingresa una dirección de correo válida.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        label="Nombre",
        help_text="Tu nombre.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        label="Apellidos",
        help_text="Tus apellidos.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tus apellidos'
        })
    )
    
    password1 = forms.CharField(
        label="Contraseña",
        help_text="Tu contraseña debe contener al menos 8 caracteres.",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    password2 = forms.CharField(
        label="Confirmar contraseña",
        help_text="Ingresa la misma contraseña que antes, para verificación.",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )
    
    def clean_username(self):
        """Validar que el username no exista en usuarios activos ni en solicitudes pendientes"""
        from django.contrib.auth.models import User
        from .models import UserRegistrationRequest
        
        username = self.cleaned_data['username']
        
        # Verificar en usuarios existentes
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        
        # Verificar en solicitudes pendientes
        if UserRegistrationRequest.objects.filter(username=username, status='pendiente').exists():
            raise forms.ValidationError("Ya existe una solicitud pendiente con este nombre de usuario.")
        
        return username
    
    def clean_email(self):
        """Validar que el email no exista en usuarios activos ni en solicitudes pendientes"""
        from django.contrib.auth.models import User
        from .models import UserRegistrationRequest
        
        email = self.cleaned_data['email']
        
        # Verificar en usuarios existentes
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        
        # Verificar en solicitudes pendientes
        if UserRegistrationRequest.objects.filter(email=email, status='pendiente').exists():
            raise forms.ValidationError("Ya existe una solicitud pendiente con este correo electrónico.")
        
        return email
    
    def clean_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return password2
    
    def clean_password1(self):
        """Validar la fortaleza de la contraseña"""
        password = self.cleaned_data.get("password1")
        
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        return password
    
    def save(self):
        """Crear una nueva solicitud de registro"""
        from django.contrib.auth.hashers import make_password
        from .models import UserRegistrationRequest
        
        # Crear hash de la contraseña
        password_hash = make_password(self.cleaned_data['password1'])
        
        # Crear la solicitud de registro
        request = UserRegistrationRequest.objects.create(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password_hash=password_hash,
            status='pendiente'
        )
        
        return request


class ItemMantenimientoForm(forms.ModelForm):
    """Formulario para cada ítem individual de mantenimiento"""
    
    # Campo personalizado para tipos de mantenimiento agrupados
    tipo_mantenimiento = TipoMantenimientoModelChoiceField(
        queryset=TipoMantenimiento.objects.none(),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-control item-tipo'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['tipo_mantenimiento'].set_user(self.user)

        if self.instance.pk and getattr(self.instance, 'registro_id', None):
            self.fields['tipo_mantenimiento'].set_vehiculo(self.instance.registro.vehiculo)
    
    class Meta:
        model = ItemMantenimiento
        fields = ['tipo_mantenimiento', 'descripcion', 'cantidad', 'costo_unitario']
        widgets = {
            'descripcion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Filtro de aceite Mann W712 (opcional)'
                }
            ),
            'cantidad': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '1',
                    'min': 1,
                    'value': 1
                }
            ),
            'costo_unitario': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00',
                    'min': 0,
                    'step': 0.01,
                    'required': True
                }
            )
        }


# Formset para manejar múltiples ítems
from django.forms import inlineformset_factory

ItemMantenimientoFormSet = inlineformset_factory(
    RegistroMantenimiento,
    ItemMantenimiento,
    form=ItemMantenimientoForm,
    extra=20,
    max_num=20,
    min_num=1,
    validate_min=True,
    can_delete=False
)

# Formset para editar mantenimientos existentes: soporta eliminación de ítems
ItemMantenimientoEditFormSet = inlineformset_factory(
    RegistroMantenimiento,
    ItemMantenimiento,
    form=ItemMantenimientoForm,
    extra=3,
    max_num=20,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class TipoTrabajoPersonalizadoForm(forms.ModelForm):
    """Formulario para crear tipos de trabajo privados del usuario."""

    class Meta:
        model = TipoMantenimiento
        fields = ['nombre', 'descripcion', 'categoria', 'vehiculos_aplicables', 'intervalo_km', 'intervalo_meses']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cambio aceite caja automática'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción opcional'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'vehiculos_aplicables': forms.Select(attrs={'class': 'form-control'}),
            'intervalo_km': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'intervalo_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['intervalo_km'].initial = 15000
        self.fields['intervalo_meses'].initial = 12

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio.')

        if self.user:
            qs = TipoMantenimiento.objects.filter(propietario=self.user, nombre__iexact=nombre)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya tienes un tipo de trabajo con ese nombre.')

        return nombre

    def clean(self):
        cleaned_data = super().clean()
        km = cleaned_data.get('intervalo_km')
        meses = cleaned_data.get('intervalo_meses')

        if (km is None or km == '') and (meses is None or meses == ''):
            cleaned_data['intervalo_km'] = 15000
            cleaned_data['intervalo_meses'] = 12

        return cleaned_data