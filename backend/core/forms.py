# ===========================================================
# 🧾 Formularios principales del módulo Core
# ===========================================================
# Este archivo define los formularios de la aplicación,
# incluyendo validaciones, widgets personalizados,
# y la integración con Google reCAPTCHA v2.
# ===========================================================

from django import forms
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Contacto, Servicio
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


# ===========================================================
# 📬 Formulario de Contacto
# ===========================================================
# Basado en el modelo `Contacto`, este formulario:
#  - Aplica estilos visuales con Tailwind CSS.
#  - Incluye un campo de selección dinámica para “Servicio”.
#  - Protege el envío mediante Google reCAPTCHA v2.
#  - Gestiona la aceptación de la política de datos (Ley 1581).
# ===========================================================
class ContactoForm(forms.ModelForm):
    """
    Formulario basado en el modelo Contacto, optimizado para Tailwind CSS
    y protegido por Google reCAPTCHA v2.
    """

    # -------------------------------------------------------
    # 🎨 Estilos base para todos los campos tipo input
    # -------------------------------------------------------
    tailwind_input_classes = (
        "w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white "
        "placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
    )

    # -------------------------------------------------------
    # 📑 Campo dinámico: tipo de servicio o solicitud
    # -------------------------------------------------------
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(is_active=True),
        label=_("Tipo de Solicitud o Servicio"),
        widget=forms.Select(attrs={'class': tailwind_input_classes})
    )

    # -------------------------------------------------------
    # 🔒 Aceptación de política de tratamiento de datos
    # -------------------------------------------------------
    acepta_politica = forms.BooleanField(
        required=True,
        label="",  # Se define dinámicamente en __init__
        widget=forms.CheckboxInput(attrs={
            'class': 'h-5 w-5 text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-600'
        })
    )

    # -------------------------------------------------------
    # 🤖 Campo reCAPTCHA (anti-bot)
    # -------------------------------------------------------
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label='')

    # -------------------------------------------------------
    # ⚙️ Configuración del modelo base
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # 🧩 Inicialización personalizada
    # -------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """
        Configura dinámicamente el formulario al instanciarlo:
        1️⃣ Aplica las clases de Tailwind CSS a cada campo.
        2️⃣ Asigna placeholders personalizados según las etiquetas.
        3️⃣ Genera dinámicamente el enlace a la Política de Datos.
        """
        super().__init__(*args, **kwargs)

        # --- 1️⃣ Aplicar clases Tailwind y placeholders ---
        meta_labels = getattr(self.Meta, 'labels', {})
        widget_fields = ['nombres', 'apellidos', 'telefono', 'correo', 'descripcion']

        for field_name in widget_fields:
            if field_name in self.fields:
                field = self.fields[field_name]
                placeholder_text = meta_labels.get(field_name, '')

                if field_name == 'descripcion':
                    # Campo de texto ampliado para mensajes
                    field.widget = forms.Textarea(attrs={
                        'class': self.tailwind_input_classes,
                        'rows': 4,
                        'placeholder': 'Ej: Necesito un sistema de inventario para mi pastelería...'
                    })
                else:
                    # Inputs estándar (texto, correo, teléfono)
                    field.widget = forms.TextInput(attrs={
                        'class': self.tailwind_input_classes,
                        'placeholder': placeholder_text
                    })

        # --- 2️⃣ Asignar dinámicamente la etiqueta de política ---
        try:
            ptdp_url = reverse("core:ptdp")
        except Exception:
            ptdp_url = "#"  # Fallback en caso de error de resolución

        self.fields['acepta_politica'].label = _(
            f'He leído, entendido y acepto los <a href="{ptdp_url}" target="_blank" '
            f'class="text-green-400 hover:text-green-300 underline font-semibold">'
            f'Términos y la Política de Tratamiento de Datos Personales</a> (Ley 1581 de 2012).'
        )
