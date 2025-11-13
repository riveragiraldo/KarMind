# =====================================================
# 📦 Importaciones generales del módulo de vistas (views.py)
# =====================================================
# Este archivo define las vistas del núcleo del sitio (core),
# incluyendo la página de contacto, autenticación y utilidades
# comunes como el manejo de correo y registros de usuario.
# =====================================================

# -----------------------------------------------------
# 🧩 Librerías de Django
# -----------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy

# -----------------------------------------------------
# 🗂️ Modelos y Formularios internos
# -----------------------------------------------------
from .models import Configuracion, Contacto, PQRSF
from .forms import ContactoForm, PQRSForm

# -----------------------------------------------------
# ⚙️ Utilidades y librerías adicionales
# -----------------------------------------------------
import threading
from core.utils import enviar_correos_contacto, enviar_correos_pqrsf


# ============================================================
# 🔗 MIXIN: Lógica Reutilizable para el Logotipo
# ============================================================
class LogoContextMixin:
    """
    Mixin que inyecta la URL del logo de la empresa ('logo_url') 
    en el contexto de cualquier Clase Basada en Vista (CBV) que la herede.
    
    Esta lógica consulta la primera fila del modelo Configuracion.
    """
    def get_context_data(self, **kwargs):
        # 1️⃣ Obtener el contexto base de la clase padre (TemplateView, por ejemplo)
        context = super().get_context_data(**kwargs)
        
        # Inicializamos la variable del logo
        logo_url = None

        try:
            # 2️⃣ Intentar recuperar la primera configuración registrada
            config = Configuracion.objects.first()
            
            # 3️⃣ Validar si la configuración existe y contiene un logo
            if config and config.logo:
                logo_url = config.logo.url

        except Configuracion.DoesNotExist:
            # ⚠️ Caso: la tabla está vacía o sin configuraciones registradas
            print("Advertencia: No se encontró la configuración del logotipo.")
        
        except Exception as e:
            # ⚙️ Captura genérica de errores inesperados
            print(f"Error al obtener la configuración: {e}")

        # 4️⃣ Agregar la URL del logo al contexto
        context['logo_url'] = logo_url
        
        # 5️⃣ Retornar el contexto completo
        return context


# ============================================================
# 🌐 Página de inicio (Landing Page)
# ============================================================
class IndexView(LogoContextMixin, TemplateView):
    """
    Clase que renderiza la página de inicio pública del sistema.
    Hereda de LogoContextMixin para inyectar el logo.
    """
    template_name = 'core/index.html'


# ============================================================
# 🌐 Página Nosotros (Landing Page)
# ============================================================
class NosotrosView(LogoContextMixin, TemplateView):
    """
    Clase que renderiza la página Nosotros pública del sistema.
    Hereda de LogoContextMixin para inyectar el logo.
    """
    template_name = 'core/nosotros.html'

# ============================================================
# 🌐 Página FAQS (Landing Page) Preguntas y Respuestas Frecuentes
# ============================================================
class FaqsView(LogoContextMixin, TemplateView):
    """
    Clase que renderiza la página Preguntas y Respuestas Frecuentes pública del sistema.
    Hereda de LogoContextMixin para inyectar el logo.
    """
    template_name = 'core/faqs.html'


# ============================================================
# 🌐 Página PTDP (Landing Page) Política de tratamiento de datos personales
# ============================================================
# La clase LogoContextMixin no está definida aquí, se asume que provee el contexto del logo.

class PtdpView(LogoContextMixin, TemplateView):
    """
    Clase que renderiza la página Política de tratamiento de datos personales pública del sistema.
    Hereda de LogoContextMixin para inyectar el logo.
    """
    template_name = 'core/ptdp.html'

    def get_context_data(self, **kwargs):
        """
        Inyecta la URL del PDF de la Política de Tratamiento de Datos Personales (PTDP)
        obtenida desde el modelo de Configuración.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Intentamos obtener la primera instancia de Configuracion
            config = Configuracion.objects.first()
            if config and config.ptdp:
                # El campo 'ptdp' debe ser un FileField o ImageField que tenga un atributo .url
                # Esta variable se usará en el HTML para el botón de descarga.
                context['ptdp_pdf_url'] = config.ptdp.url
            else:
                context['ptdp_pdf_url'] = None
        except Exception as e:
            # En caso de que el modelo no exista o haya un error de base de datos
            print(f"Error al obtener la configuración PTDP: {e}")
            context['ptdp_pdf_url'] = None
            
        return context

# ============================================================
# 🌐 Página Términos de servicio (Landing Page) 
# ============================================================
class TerminosServicioView(LogoContextMixin, TemplateView):
    """
    Clase que renderiza la página Términos de servicio pública del sistema.
    Hereda de LogoContextMixin para inyectar el logo.
    """
    template_name = 'core/terminos_servicio.html'


# ============================================================
# 🌐 Página Acerca de este sitio web (Landing Page) 
# ============================================================
class AcercaDeView(LogoContextMixin, TemplateView):
    """
    Clase que renderiza la página Términos de servicio pública del sistema.
    Hereda de LogoContextMixin para inyectar el logo.
    """
    template_name = 'core/acerca_de.html'





# ============================================================
# 🌐 Página Contacto (Landing Page) 
# ============================================================
class ContactoView(LogoContextMixin, FormView):
    """
    Renderiza la página de contacto, guarda la información del usuario
    y registra evidencia técnica del consentimiento digital (IP, user_agent, fecha, hash).
    """
    template_name = 'core/contacto.html'
    form_class = ContactoForm
    success_url = reverse_lazy('core:contacto')

    def form_valid(self, form):
        """
        Guarda la instancia de Contacto y lanza el envío de correos en un hilo separado.
        """
        try:
            # ==========================================================
            # 1️⃣ Crear instancia sin guardar aún para poder modificarla
            # ==========================================================
            contacto_instance = form.save(commit=False)

            # Capturar IP del visitante
            contacto_instance.ip_autorizacion = self.get_client_ip()

            # Capturar información del navegador/dispositivo
            contacto_instance.user_agent = self.request.META.get('HTTP_USER_AGENT', 'Desconocido')

            # Registrar fecha de consentimiento (si no existe)
            if not contacto_instance.fecha_autorizacion and contacto_instance.acepta_politica:
                contacto_instance.fecha_autorizacion = timezone.now()

            # Guardar finalmente en la base de datos (esto también genera el hash)
            contacto_instance.save()

            # ==========================================================
            # 2️⃣ Enviar correos en segundo plano
            # ==========================================================
            correo_thread = threading.Thread(
                target=enviar_correos_contacto,
                args=(contacto_instance,),
                daemon=True  # 🔹 para que no bloquee el cierre del servidor si algo queda pendiente
            )
            correo_thread.start()

            # ==========================================================
            # 3️⃣ Mensaje inmediato al usuario (sin esperar al envío)
            # ==========================================================
            messages.success(
                self.request,
                '¡Mensaje recibido! Gracias por contactarnos. '
                'Nuestro equipo revisará tu solicitud y te responderá pronto.'
            )

        except Exception as e:
            # Capturamos cualquier fallo crítico (base de datos, correo, etc.)
            messages.error(
                self.request,
                'Hubo un error crítico al guardar tu solicitud. Por favor, inténtalo de nuevo más tarde.'
            )
            print(f"❌ Error al procesar solicitud de contacto: {e}")
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_client_ip(self):
        """
        Obtiene la IP real del cliente, compatible con servidores detrás de proxy o Cloudflare.
        """
        request = self.request
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

    def form_invalid(self, form):
        """
        Se ejecuta cuando el formulario (POST) es inválido.
        """
        messages.error(
            self.request,
            'No fue posible enviar tu solicitud. Por favor, revisa los campos marcados en rojo '
            'y verifica si el reCAPTCHA fue completado correctamente.'
        )
        return super().form_invalid(form)





# ============================================================
# 🌐 Página PQRSF (Landing Page) 
# ============================================================
class PQRSFView(LogoContextMixin, FormView):
    """
    Renderiza la página de PQRSF y gestiona el envío del formulario.
    Registra evidencia técnica del consentimiento digital.
    """
    template_name = 'core/pqrsf.html'
    form_class = PQRSForm
    success_url = reverse_lazy('core:pqrsf')

    # ------------------------------------------------------------
    # ✅ Procesamiento de formulario válido
    # ------------------------------------------------------------
    def form_valid(self, form):
        """
        Guarda la instancia de PQRSF y lanza el envío de correos
        en un hilo separado para no bloquear la respuesta.
        """
        try:
            # 1️⃣ Crear instancia sin guardar aún
            pqrsf_instance = form.save(commit=False)

            # 2️⃣ Registrar IP, agente y fecha de consentimiento
            pqrsf_instance.ip_autorizacion = self.get_client_ip()
            pqrsf_instance.user_agent = self.request.META.get('HTTP_USER_AGENT', 'Desconocido')

            if not pqrsf_instance.fecha_autorizacion and pqrsf_instance.acepta_politica:
                pqrsf_instance.fecha_autorizacion = timezone.now()

            # 3️⃣ Guardar con archivo adjunto si lo hay
            pqrsf_instance.save()

            # 4️⃣ Envío de correos en segundo plano
            correo_thread = threading.Thread(
                target=enviar_correos_pqrsf,
                args=(pqrsf_instance,),
                daemon=True
            )
            correo_thread.start()

            # 5️⃣ Notificación al usuario
            messages.success(
                self.request,
                '¡Mensaje recibido! Gracias por contactarnos. '
                'Nuestro equipo revisará tu solicitud y te responderá pronto.'
            )

        except Exception as e:
            print(f"❌ Error al procesar solicitud de PQRSF: {e}")
            messages.error(
                self.request,
                'Hubo un error crítico al guardar tu solicitud. '
                'Por favor, inténtalo de nuevo más tarde.'
            )
            return super().form_invalid(form)

        return super().form_valid(form)

    # ------------------------------------------------------------
    # ⚙️ Manejo de IP del cliente
    # ------------------------------------------------------------
    def get_client_ip(self):
        """
        Obtiene la IP real del cliente, considerando servidores proxy.
        """
        request = self.request
        headers = [
            'HTTP_CF_CONNECTING_IP',   # Cloudflare
            'HTTP_X_FORWARDED_FOR',    # Proxies estándar
            'HTTP_X_REAL_IP',          # Nginx o similares
            'REMOTE_ADDR',             # Fallback local
        ]
        for header in headers:
            ip = request.META.get(header)
            if ip:
                return ip.split(',')[0].strip()
        return '0.0.0.0'

    # ------------------------------------------------------------
    # 🚫 Manejo de formulario inválido
    # ------------------------------------------------------------
    def form_invalid(self, form):
        """
        Muestra mensaje de error si el formulario tiene fallos.
        """
        messages.error(
            self.request,
            'No fue posible enviar tu solicitud. '
            'Revisa los campos marcados y asegúrate de completar el reCAPTCHA.'
        )
        return super().form_invalid(form)

    # ------------------------------------------------------------
    # ⚙️ Incluir request.FILES para manejar adjuntos
    # ------------------------------------------------------------
    def post(self, request, *args, **kwargs):
        """
        Sobrescribe el método POST para incluir archivos adjuntos.
        """
        form = self.get_form()
        form = PQRSForm(request.POST, request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)



def login_view(request):
    """
    Maneja el inicio de sesión de usuarios.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}')
            return redirect('core:home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'core/login.html')

def logout_view(request):
    """
    Cierra sesión del usuario actual y lo redirige al inicio.
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('core:home')



# ============================================================
# 🌐 ¿Olvidó su contraseña? (Landing Page) 
# ============================================================
# Importaciones necesrias para restablecimiento de contraseña
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
from .forms import CustomPasswordResetForm
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.http import HttpResponseRedirect, QueryDict
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode

from django.contrib.auth import login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
UserModel = get_user_model()
from django.shortcuts import resolve_url
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from .forms import CustomSetPasswordForm



class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {"title": self.title, "subtitle": None, **(self.extra_context or {})}
        )
        return context




class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = "emails/password_reset_email.html"
    extra_email_context = None
    
    from_email = "KarMind | Password<noreply@karmind.co>"
    html_email_template_name = None
    subject_template_name = "core/password_reset_subject.txt"
    success_url = reverse_lazy("core:password_reset_done_reactivos")
    template_name = "core/password_reset.html"
    title = ("Password reset")
    # title = _("Password reset")
    token_generator = default_token_generator
    

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)
    
class CustomPasswordResetView(LogoContextMixin, PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "core/password_reset.html"
    success_url = reverse_lazy("core:password_reset_done")
    from_email = "KarMind | Password<noreply@karmind.co>"
    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "core/password_reset_subject.txt"
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_invalid(self, form):
        messages.error(self.request, "No se pudo restablecer la contraseña. Verifica la información e inténtalo nuevamente.")
        return super().form_invalid(form)

    def form_valid(self, form):
        # Ejecuta el envío una sola vez
        form.save(
            use_https=self.request.is_secure(),
            token_generator=self.token_generator,
            from_email=self.from_email,
            email_template_name=self.email_template_name,
            subject_template_name=self.subject_template_name,
            request=self.request,
            html_email_template_name=self.html_email_template_name,
            extra_email_context=self.extra_email_context,
        )
        # Luego redirige sin llamar al padre (para evitar duplicado)
        return HttpResponseRedirect(self.get_success_url())



INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"


class PasswordResetDoneView(LogoContextMixin,PasswordContextMixin, TemplateView):
    template_name = "core/password_reset_done.html"
    title = ("Password reset sent")
    # title = _("Password reset sent")


class PasswordResetConfirmView(LogoContextMixin,PasswordContextMixin, FormView):
    form_class = CustomSetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = "set-password"
    success_url = reverse_lazy("core:password_reset_complete")
    template_name = "core/password_reset_confirmation.html"
    title = ("Enter new password")
    # title = _("Enter new password")
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            UserModel.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    # "title": _("Password reset unsuccessful"),
                    "title": ("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context




class PasswordResetCompleteView(LogoContextMixin,PasswordContextMixin, TemplateView):
    template_name = "core/password_reset_complete.html"
    title = ("Password reset complete")
    # title = _("Password reset complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = resolve_url(settings.LOGIN_URL)
        return context