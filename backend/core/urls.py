# ============================================
# Enrutamiento principal de la app Core.
# Maneja la página de inicio y autenticación.
# ============================================

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]