# =====================================================
# 📦 Importaciones generales del módulo de vistas (views.py)
# =====================================================
# Este archivo define las vistas del núcleo del sitio (admin_appa),
# =====================================================

# -----------------------------------------------------
# 🧩 Librerías de Django
# -----------------------------------------------------

from django.views.generic import TemplateView
# -----------------------------------------------------
# 🗂️ Modelos y Formularios internos
# -----------------------------------------------------
from core.models import Configuracion


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
    template_name = 'admin_app/index.html'