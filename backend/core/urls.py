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
app_name = 'core'

# -----------------------------------------------------
# 🚏 Definición de rutas principales
# -----------------------------------------------------
urlpatterns = [
    # Páginas informativas y principales
    path('', views.IndexView.as_view(), name='home'),
    path('nosotros', views.NosotrosView.as_view(), name='nosotros'),
    path('faqs', views.FaqsView.as_view(), name='faqs'),
    path('ptdp', views.PtdpView.as_view(), name='ptdp'),  # Política de Tratamiento de Datos Personales
    path('terminos-servicio', views.TerminosServicioView.as_view(), name='terminos_servicio'),
    path('acerca-de', views.AcercaDeView.as_view(), name='acerca_de'),

    # Página de contacto y pqrsf (formulario con envío de correos)
    path('contacto', views.ContactoView.as_view(), name='contacto'),
    path('pqrs', views.PQRSFView.as_view(), name='pqrsf'),

    # Autenticación de usuarios
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
