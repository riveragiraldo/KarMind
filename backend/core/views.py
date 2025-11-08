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

