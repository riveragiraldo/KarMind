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
def general_send_mail(
    asunto, destinatarios, mensaje_html, remitente=None, archivos_adjuntos=None
):
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
        print("Remitente que llega a la función: ", remitente)
        # Determinar remitente final
        if not remitente:
            remitente_final = "KarMind <no-reply@karmind.co>"
        elif "<" in remitente and ">" in remitente:
            remitente_final = remitente.strip()
        else:
            remitente_final = f"{remitente} <{settings.DEFAULT_FROM_EMAIL}>"
        print("Remitente que se envía: ", remitente_final)

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
        fecha_local = timezone.localtime(contacto.fecha_creacion).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        ip_origen = contacto.ip_autorizacion

        # ----------------------------------------------------
        # 🔗 GENERACIÓN DE URLs ABSOLUTAS (CAMBIO CLAVE)
        # ----------------------------------------------------
        # protocol = 'https' if self.request.is_secure() else 'http'
        # domain = self.request.get_host()
        # 1. URL de la Política de Tratamiento de Datos Personales (PTDP)
        try:
            # Usar build_absolute_uri para incluir protocolo y dominio
            ptdp_path = reverse("core:ptdp")
            ptdp_url = request.build_absolute_uri(ptdp_path) if request else ptdp_path
        except Exception as e:
            print(f"Error al generar PTDP URL: {e}")
            ptdp_url = "#"  # Fallback

        # 2. URL del CTA de Administrador (para responder la solicitud)
        try:
            # La URL de respuesta es tipicamente '/admin/contacto/{pk}/'
            admin_cta_path = reverse(
                "core:contacto", args=[contacto.pk]
            )  # Asumo esta es la URL de admin

            # Usar build_absolute_uri para obtener la URL absoluta
            admin_cta_url = (
                request.build_absolute_uri(admin_cta_path) if request else "#"
            )

            # Si no puedes usar 'admin:appname_contacto_change', usa la ruta literal:
            # admin_cta_url = request.build_absolute_uri(f"/admin/contacto/{contacto.pk}/") if request else "#"

        except Exception as e:
            print(f"Error al generar Admin CTA URL: {e}")
            # Si falla (ej. sin request), usamos un placeholder que debería ser editado manualmente
            admin_cta_url = (
                f"https://DEBES-PROPORCIONAR-REQUEST/admin/contacto/{contacto.pk}/"
            )

        # =====================================================
        # 🧩 MENSAJE PARA ADMINISTRADOR
        # =====================================================
        mensaje_admin_str = """
            <!-- Bloque de Alerta Principal -->
    <h1 class="kar-h1" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 24px; font-weight: 700; margin: 0 0 20px 0;">
        <span style="color: #10B981;">¡Nuevo Contacto Recibido!</span>
    </h1>
    
    <p class="kar-p" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
        Un usuario ha completado el formulario de contacto en el sitio web y requiere una respuesta.
    </p>

    <!-- Tarjeta de Datos de Contacto (Estilo KarMind) -->
    <table border="0" cellpadding="10" cellspacing="0" width="100%" style="background-color: #2D3748; border-radius: 8px; margin-bottom: 20px;">
        <tr style="background-color: #334155; border-radius: 8px 8px 0 0;">
            <td colspan="2">
                <p class="kar-h2" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 16px; font-weight: 700; margin: 0;">
                    Detalles del Solicitante
                </p>
            </td>
        </tr>
        <tr>
            <td class="kar-data-label" width="30%" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-weight: 600; font-size: 14px;">Nombre:</td>
            <td class="kar-data-value" width="70%" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-weight: 400; font-size: 14px;">{{contacto.nombres}} {{contacto.apellidos}}</td>
        </tr>
        
        <tr>
            <td class="kar-data-label" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-weight: 600; font-size: 14px;">Email:</td>
            <td class="kar-data-value" style="font-family: 'Inter', sans-serif; color: #3B82F6; font-weight: 400; font-size: 14px;"><a href="mailto:{{contacto.correo}}" class="kar-link" style="color: #3B82F6;">{{contacto.correo}}</a></td>
        </tr>
        <tr>
            <td class="kar-data-label" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-weight: 600; font-size: 14px;">Teléfono:</td>
            <td class="kar-data-value" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-weight: 400; font-size: 14px;">{{contacto.telefono}}</td>
        </tr>
        <tr>
            <td class="kar-data-label" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-weight: 600; font-size: 14px;">Asunto:</td>
            <td class="kar-data-value" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-weight: 400; font-size: 14px;">{{contacto.servicio}}</td>
        </tr>
    </table>
    
    <!-- Bloque de Mensaje -->
    <p class="kar-h2" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 18px; font-weight: 700; margin: 0 0 10px 0;">
        Mensaje del Usuario:
    </p>
    <div style="background-color: #0F172A; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 25px;">
        <p class="kar-p" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 15px; line-height: 1.6; margin: 0;">
            {{contacto.descripcion}}
        </p>
    </div>

    <!-- CTA para Administrador -->
    <p style="text-align: center;">
        <a href="{{admin_cta_url}}" target="_blank" class="kar-btn-accent" style="background-color: #10B981; border-radius: 8px; color: #1F2937; display: inline-block; font-size: 16px; font-weight: 700; padding: 12px 24px; text-align: center; text-decoration: none; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.4);">
            Responder a la Solicitud
        </a>
    </p>
        """
        mensaje_admin_render = Template(mensaje_admin_str).render(
            Context(
                {
                    "contacto": contacto,
                    "fecha_local": fecha_local,
                    "ip_origen": ip_origen,
                }
            )
        )
        cuerpo_admin_html = render_to_string(
            "emails/base_email.html", {"mensaje": mensaje_admin_render}
        )

        # =====================================================
        # 🧩 MENSAJE PARA USUARIO (ACUSE DE RECIBIDO)
        # =====================================================
        mensaje_usuario_str = """
            <!-- Bloque de Título y Agradecimiento -->
    <h1 class="kar-h1" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 24px; font-weight: 700; margin: 0 0 20px 0;">
        ¡Hola {{contacto.nombres}}!
    </h1>
    
    <p class="kar-p" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
        Hemos recibido tu mensaje correctamente y estamos listos para revisar tu solicitud. Agradecemos tu interés en <span style="color: #3B82F6; font-weight: 600;">KarMind</span>.
    </p>
    
    <!-- Tarjeta de Confirmación de Datos Enviados -->
    <div style="background-color: #2D3748; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
        <p class="kar-h2" style="font-family: 'Inter', sans-serif; color: #10B981; font-size: 16px; font-weight: 700; margin: 0 0 10px 0;">
            Tu mensaje enviado:
        </p>
        <p class="kar-p" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 15px; line-height: 1.6; margin: 0;">
            {{contacto.descripcion}}
        </p>
    </div>
    
    <!-- Bloque de Próximos Pasos -->
    <p class="kar-h2" style="font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 18px; font-weight: 700; margin: 0 0 10px 0;">
        ¿Qué sigue ahora?
    </p>
    <ul style="padding-left: 20px; margin: 0 0 30px 0;">
        <li class="kar-p" style="font-family: 'Inter', sans-serif; color: #94A3B8; font-size: 15px; line-height: 1.6; margin-bottom: 8px;">
            Un integrante de nuestro equipo revisará tu solicitud y te contactará proximamente para atender tu solicitud.
        </li>
        
    </ul>

    <!-- Footer para el Hash Legal -->
    <div style="background-color: #0F172A; padding: 10px; border-radius: 6px; text-align: center;">
        <p class="kar-footer" style="color: #475569; font-size: 12px; line-height: 1.5; margin: 0;">
            ID de Transacción Legal:<br>
            <span style="color: #94A3B8; font-family: monospace; font-size: 11px; word-break: break-all;">
                {{ contacto.consentimiento_hash }} - {{ contacto.fecha_autorizacion }}
            </span>
            <br>
            Navegador y Dirección IP:<br>
            <span style="color: #94A3B8; font-family: monospace; font-size: 11px; word-break: break-all;">
                {{ contacto.ip_autorizacion }} - {{ contacto.user_agent }}
            </span>
            <br>
            Puedes consultar nuestra <a href="{{ptdp_url}}" style="color: #475569;">Política de Datos Personales</a>.
        </p>
    </div>
        """
        mensaje_usuario_render = Template(mensaje_usuario_str).render(
            Context(
                {
                    "contacto": contacto,
                    "fecha_local": fecha_local,
                    "ip_origen": ip_origen,
                    "ptdp_url": ptdp_url,
                }
            )
        )
        cuerpo_usuario_html = render_to_string(
            "emails/base_email.html", {"mensaje": mensaje_usuario_render}
        )

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
        print(
            f"❌ Error al procesar correos de contacto #{getattr(contacto, 'id', 'n/a')}: {e}"
        )
        return False
