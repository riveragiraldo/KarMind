# ============================================
# Enrutamiento principal de la app Core.
# Maneja la página de inicio y autenticación.
# ============================================

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('nosotros', views.NosotrosView.as_view(), name='nosotros'),
    path('faqs', views.FaqsView.as_view(), name='faqs'),
    path('ptdp', views.PtdpView.as_view(), name='ptdp'),
    path('terminos-servicio', views.TerminosServicioView.as_view(), name='terminos_servicio'),
    path('acerca-de', views.AcercaDeView.as_view(), name='acerca_de'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

