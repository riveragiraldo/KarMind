
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from core.models import Configuracion
from django.urls import reverse
from django.utils import timezone


# ------------------------------------------------------------
# 🧩 Función genérica para envío de correos HTML con adjuntos
# ------------------------------------------------------------
def general_send_mail(asunto, destinatarios, mensaje_html, remitente=None, archivos_adjuntos=None):
    """
    Envía un correo con versión HTML y texto plano.

    Parámetros:
        - asunto (str): Asunto del correo.
        - destinatarios (list): Lista de correos destino.
        - mensaje_html (str): Cuerpo del correo en formato HTML.
        - remitente (str, opcional): 
              * Puede ser solo el nombre (ej. "Pedidos Karamba") → usa DEFAULT_FROM_EMAIL.
              * O nombre + correo (ej. "Pedidos Karamba <pedidos@karamba.com>").
              * Si no se pasa, se usa "KarMind <no-reply@karmind.co>".
        - archivos_adjuntos (list, opcional): Lista de rutas absolutas o File-like objects a adjuntar.

    Retorna:
        - True si el correo fue enviado correctamente, False si falló.
    """
    try:
        print("Remitente que llega a la función: ",remitente)
        # Determinar remitente final
        if not remitente:
            remitente_final = "KarMind <no-reply@karmind.co>"
        elif "<" in remitente and ">" in remitente:
            remitente_final = remitente.strip()
        else:
            remitente_final = f"{remitente} <{settings.DEFAULT_FROM_EMAIL}>"
        print("Remitente que se envía: ",remitente_final)

        cuerpo_txt = strip_tags(mensaje_html)

        email = EmailMultiAlternatives(
            subject=asunto,
            body=cuerpo_txt,
            from_email=remitente_final,
            to=destinatarios,
        )
        email.attach_alternative(mensaje_html, "text/html")

        # Adjuntar archivos (si existen)
        if archivos_adjuntos:
            for archivo in archivos_adjuntos:
                try:
                    email.attach_file(archivo)
                except Exception as e:
                    print(f"⚠️ No se pudo adjuntar el archivo '{archivo}': {e}")

        email.send(fail_silently=False)
        return True

    except Exception as e:
        print(f"❌ Error al enviar correo '{asunto}': {e}")
        return False


# ------------------------------------------------------------
# 📨 Envío de correos de contacto (Admin + Usuario)
# ------------------------------------------------




def enviar_correos_contacto(contacto, request=None):
    """
    Envía los correos relacionados con una solicitud de contacto:
    1️⃣ Al administrador (detalles completos)
    2️⃣ Al usuario (acuse de recibido con nota legal)

    Parámetros:
    - contacto: instancia del modelo Contacto
    - request (opcional): para obtener IP y hora local del navegador
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

        # ----------------------------------------------------
        # 📅 Fecha y IP (si request está disponible)
        # ----------------------------------------------------
        fecha_local = timezone.localtime(contacto.fecha_creacion).strftime("%d/%m/%Y %H:%M:%S")
        ip_origen = contacto.ip_autorizacion

        # URL de política
        try:
            ptdp_url = request.build_absolute_uri(reverse("core:ptdp")) if request else reverse("core:ptdp")
        except Exception:
            ptdp_url = "#"

        # =====================================================
        # 🧩 MENSAJE PARA ADMINISTRADOR
        # =====================================================
        mensaje_admin_str = """
            <h2>📩 Nueva solicitud de contacto</h2>
            <p><strong>ID:</strong> {{ contacto.id }}</p>
            <p><strong>Fecha:</strong> {{ fecha_local }}</p>
            <p><strong>Nombre:</strong> {{ contacto.nombres }} {{ contacto.apellidos }}</p>
            <p><strong>Teléfono:</strong> {{ contacto.telefono }}</p>
            <p><strong>Email:</strong> {{ contacto.correo }}</p>
            <p><strong>Servicio solicitado:</strong> {{ contacto.servicio.nombre }}</p>
            <p><strong>Descripción:</strong><br>{{ contacto.descripcion }}</p>
            <p><strong>IP de origen:</strong> {{ ip_origen }}</p>
            <hr>
            <p><em>Este mensaje fue generado automáticamente por el sistema KarMind.</em></p>
        """
        mensaje_admin_render = Template(mensaje_admin_str).render(
            Context({'contacto': contacto, 'fecha_local': fecha_local, 'ip_origen': ip_origen})
        )
        cuerpo_admin_html = render_to_string('emails/contacto_admin.html', {'mensaje': mensaje_admin_render})

        # =====================================================
        # 🧩 MENSAJE PARA USUARIO (ACUSE DE RECIBIDO)
        # =====================================================
        mensaje_usuario_str = """
            <h2>✅ Hemos recibido tu solicitud</h2>
            <p>Hola {{ contacto.nombres }},</p>
            <p>Gracias por contactarte con <strong>KarMind</strong>.</p>
            <p>Tu solicitud ha sido registrada con el número <strong>#{{ contacto.id }}</strong>.</p>
            <p>Un integrante de nuestro equipo revisará tu mensaje y te contactará pronto.</p>

            <hr style="margin:20px 0; border-top:1px solid #444;">

            <p style="font-size:13px; color:#ccc;">
                Con la recepción de este correo confirmas que aceptaste nuestra
                <a href="{{ ptdp_url }}" target="_blank" style="color:#6ee7b7;">Política de Tratamiento de Datos Personales</a>,
                conforme a la Ley 1581 de 2012.
            </p>
            <p style="font-size:11px; color:#888;">
                📅 Fecha y hora de registro: {{ fecha_local }}<br>
                📅 Acepta Política de Tratamiento de Datos Personales: {{ contacto.acepta_politica }}<br>
                🌐 Navegador: {{ fecha_local }}<br>
                🖥️ IP registrada: {{ ip_origen }}<br>
                🪪 Firma Digital: {{ contacto.consentimiento_hash }}
            </p>

            <p style="font-size:12px; color:#999; margin-top:15px;">
                <em>Por favor, no respondas a este correo. Fue generado automáticamente por el sistema KarMind.</em>
            </p>
        """
        mensaje_usuario_render = Template(mensaje_usuario_str).render(
            Context({
                'contacto': contacto,
                'fecha_local': fecha_local,
                'ip_origen': ip_origen,
                'ptdp_url': ptdp_url
            })
        )
        cuerpo_usuario_html = render_to_string('emails/contacto_admin.html', {'mensaje': mensaje_usuario_render})

        # =====================================================
        # 🚀 ENVÍO DE CORREOS
        # =====================================================
        remitente = "Contacto Web KarMind <no-reply@karmind.co>"

        general_send_mail(
            asunto=f"📩 Nueva solicitud de contacto #{contacto.id}",
            destinatarios=[admin_email],
            mensaje_html=cuerpo_admin_html,
            remitente=remitente,
        )

        general_send_mail(
            asunto=f"KarMind | Confirmación de tu solicitud #{contacto.id}",
            destinatarios=[user_email],
            mensaje_html=cuerpo_usuario_html,
            remitente=remitente,
        )

        print(f"✅ Correos enviados correctamente para el contacto #{contacto.id}")
        return True

    except Exception as e:
        print(f"❌ Error al procesar correos de contacto #{getattr(contacto, 'id', 'n/a')}: {e}")
        return False
