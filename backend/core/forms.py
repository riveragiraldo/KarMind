from django import forms
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Contacto, Servicio

# 1. Importar el campo de reCAPTCHA

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class ContactoForm(forms.ModelForm):
    """
    Formulario basado en el modelo Contacto, optimizado para Tailwind CSS
    y protegido por Google reCAPTCHA v2.
    """

    # Clases de Tailwind para aplicar a todos los campos
    tailwind_input_classes = (
        "w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white "
        "placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
    )
    
    # 1. Definir los campos que heredan del modelo
    
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(is_active=True), 
        label=_("Tipo de Solicitud o Servicio"),
        widget=forms.Select(attrs={'class': tailwind_input_classes})
    )

    acepta_politica = forms.BooleanField(
        required=True,
        label="", # Se asigna dinámicamente en __init__
        widget=forms.CheckboxInput(attrs={
            'class': 'h-5 w-5 text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-600'
        })
    )
    # -------------------------------------------------
    # 🛡️ CAMPO reCAPTCHA (Anti-Bot)
    # -------------------------------------------------
    # Reemplazamos el Honeypot con el campo de reCAPTCHA
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label='') 
    # -------------------------------------------------


    class Meta:
        model = Contacto
        fields = [
            'nombres',
            'apellidos',
            'telefono',
            'correo',
            'servicio',
            'descripcion',
            'acepta_politica',
        ]
        labels = {
            'nombres': _('Tus Nombres'),
            'apellidos': _('Tus Apellidos (Opcional)'),
            'telefono': _('Teléfono de Contacto'),
            'correo': _('Tu Correo Electrónico'),
            'descripcion': _('Cuéntanos sobre tu necesidad (Máx. 200 caracteres)'),
        }

    def __init__(self, *args, **kwargs):
        """
        Sobrescribimos el init para:
        1. Aplicar las clases de Tailwind a los campos.
        2. Asignar el label de 'acepta_politica' en tiempo de ejecución.
        """
        super().__init__(*args, **kwargs)
        
        # --- 1. APLICAR CLASES TAILWIND (CORREGIDO) ---
        
        # Obtenemos el diccionario de labels de la clase Meta de forma segura
        meta_labels = getattr(self.Meta, 'labels', {})

        widget_fields = ['nombres', 'apellidos', 'telefono', 'correo', 'descripcion']
        
        for field_name in widget_fields:
            if field_name in self.fields:
                field = self.fields[field_name]
                
                # Obtenemos el texto del label desde Meta para usarlo como placeholder
                placeholder_text = meta_labels.get(field_name, '')

                if field_name == 'descripcion':
                    # Usamos un placeholder específico y más útil para el textarea
                    field.widget = forms.Textarea(attrs={
                        'class': self.tailwind_input_classes,
                        'rows': 4, 
                        'placeholder': 'Ej: Necesito un sistema de inventario para mi pastelería...'
                    })
                else:
                    # Usamos el texto del label como placeholder para los inputs
                    field.widget = forms.TextInput(attrs={
                        'class': self.tailwind_input_classes,
                        'placeholder': placeholder_text
                    })
        
        # --- 2. ASIGNACIÓN DINÁMICA DE LABEL (Arreglo de Importación Circular) ---
        try:
            ptdp_url = reverse("core:ptdp")
        except Exception:
            ptdp_url = "#" # Fallback
            
        self.fields['acepta_politica'].label = _(
            f'He leído, entendido y acepto los <a href="{ptdp_url}" target="_blank" class="text-green-400 hover:text-green-300 underline font-semibold">Términos y la Política de Tratamiento de Datos Personales</a> (Ley 1581 de 2012).'
        )