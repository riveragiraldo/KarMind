from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.views.generic import TemplateView
from .models import Configuracion


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

