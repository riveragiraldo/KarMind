# =====================================================
# 🌐 Enrutamiento principal de la aplicación Core
# =====================================================
# Este archivo define las rutas base del sitio web,
# incluyendo la página de inicio, secciones informativas,
# política de datos, contacto y autenticación de usuarios.
# =====================================================

from django.urls import path
from . import views

# Nombre de espacio (namespace) para las rutas de esta app
app_name = 'surprise_app'

# -----------------------------------------------------
# 🚏 Definición de rutas principales
# -----------------------------------------------------
urlpatterns = [
    # Páginas informativas y principales
    path('', views.IndexView.as_view(), name='surprise_home'),
    
]