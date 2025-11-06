# core/utils/correos_contacto.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import Template, Context
from django.utils.html import strip_tags
from django.conf import settings
from core.models import Configuracion

def enviar_correos_contacto(contacto):
    """
    Envía correo al admin y acuso al usuario. Aquí renderizamos una
    plantilla HTML dinámica contenida en la variable 'mensaje'.
    """
    try:
        config = Configuracion.objects.first()
        if not config or not config.email_administrativo:
            print("⚠️ No se encontró email_administrativo en Configuración.")
            return False

        admin_email = config.email_administrativo.strip()
        user_email = contacto.correo.strip() if contacto.correo else None
        if not user_email:
            print(f"⚠️ Contacto #{contacto.id} no tiene correo válido.")
            return False

        # ------------------------------------------------------------------
        # Construcción del 'mensaje' como string que incluye variables Django para el admin
        # ------------------------------------------------------------------
        mensaje = (
            '<h2>Nueva solicitud de contacto</h2>'
            '<p><strong>ID:</strong> {{ contacto.id }}</p>'
            '<p><strong>Fecha:</strong> {{ contacto.fecha_creacion|date:"d/m/Y H:i" }}</p>'
            '<p><strong>Nombre:</strong> {{ contacto.nombres }} {{ contacto.apellidos }}</p>'
            '<p><strong>Teléfono:</strong> {{ contacto.telefono }}</p>'
            '<p><strong>Email:</strong> {{ contacto.correo }}</p>'
            '<p><strong>Servicio solicitado:</strong> {{ contacto.servicio.nombre }}</p>'
            '<p><strong>Descripción:</strong><br>{{ contacto.descripcion }}</p>'
            '<p><em>Este mensaje fue generado automáticamente por el sistema KarMind.</em></p>'
        )

        # --------------------------------------------------------
        # 1) Renderizamos la 'sub-plantilla' desde la cadena (mensaje)
        # --------------------------------------------------------
        # Esto evalúa las variables como {{ contacto... }} correctamente.
        mensaje_template = Template(mensaje)
        mensaje_rendered = mensaje_template.render(Context({'contacto': contacto, 'config': config}))

        # --------------------------------------------------------
        # 2) Renderizamos la plantilla final del correo del admin,
        # pasando 'mensaje_rendered'. En la plantilla se debe usar
        # {{ mensaje|safe }} para no escapar el HTML ya renderizado.
        # --------------------------------------------------------
        contexto_admin = {'mensaje': mensaje_rendered, 'contacto': contacto, 'config': config}
        cuerpo_admin_html = render_to_string('emails/base_email.html', contexto_admin)
        cuerpo_admin_txt = strip_tags(cuerpo_admin_html)

        # --------------------------------------------------------
        # Correo al solicitante — usamos plantilla separada
        # --------------------------------------------------------
        asunto_usuario = f"KarMind | Confirmación de tu solicitud #{contacto.id}"
        # ------------------------------------------------------------------
        # Construcción del 'mensaje' como string que incluye variables Django para el usuario
        # ------------------------------------------------------------------
        mensaje_usuario = (
            '<h2>✅ Hemos recibido tu solicitud</h2>'
            '<p>Hola {{ contacto.nombres }},</p>'
            '<p>Gracias por contactarte con <strong>KarMind</strong>.</p>'
            '<p>Tu solicitud ha sido registrada con el número <strong>#{{ contacto.id }}</strong>.</p>'
            '<p>Uno de nuestros asesores revisará tu solicitud y te contactará pronto.</p>'
            '<p><em>Por favor no respondas a este correo, fue generado automáticamente.</em></p>'
        )

        # --------------------------------------------------------
        # 1) Renderizamos la 'sub-plantilla' desde la cadena (mensaje)
        # --------------------------------------------------------
        # Esto evalúa las variables como {{ contacto... }} correctamente.
        mensaje_template = Template(mensaje_usuario)
        mensaje_rendered = mensaje_template.render(Context({'contacto': contacto, 'config': config}))

        # --------------------------------------------------------
        # 2) Renderizamos la plantilla final del correo del admin,
        # pasando 'mensaje_rendered'. En la plantilla se debe usar
        # {{ mensaje|safe }} para no escapar el HTML ya renderizado.
        # --------------------------------------------------------
        contexto_usuario = {'mensaje': mensaje_rendered, 'contacto': contacto, 'config': config}
        cuerpo_usuario_html = render_to_string('emails/base_email.html', contexto_usuario)
        cuerpo_usuario_txt = strip_tags(cuerpo_admin_html)

        # ========================================================
        # Envío de correos (admin y usuario)
        # ========================================================
        # Admin
        asunto_admin = f"📩 Nueva solicitud de contacto #{contacto.id}"
        email_admin = EmailMultiAlternatives(
            asunto_admin,
            cuerpo_admin_txt,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
        )
        email_admin.attach_alternative(cuerpo_admin_html, "text/html")
        email_admin.send(fail_silently=False)

        # Usuario
        email_user = EmailMultiAlternatives(
            asunto_usuario,
            cuerpo_usuario_txt,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
        )
        email_user.attach_alternative(cuerpo_usuario_html, "text/html")
        email_user.send(fail_silently=False)

        print(f"✅ Correos enviados correctamente para el contacto #{contacto.id}")
        return True

    except Exception as e:
        print(f"❌ Error al enviar correos de contacto #{getattr(contacto, 'id', 'n/a')}: {e}")
        return False
