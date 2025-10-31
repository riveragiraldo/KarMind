# ============================================================
# Vistas base de la aplicación principal (core).
# Incluye la página de inicio pública y el login/logout.
# ============================================================

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone

def home_view(request):
    """
    Vista principal que renderiza la interfaz del frontend.
    """
   
    return render(request, 'core/index.html')



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

