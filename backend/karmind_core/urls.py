# ===============================================================
# 🌐 ARCHIVO DE RUTAS PRINCIPAL - KarMind
# ===============================================================
# Este archivo define la configuración central de enrutamiento del
# proyecto KarMind. Incluye las rutas administrativas, los módulos
# internos y la configuración para servir archivos multimedia en
# entornos de desarrollo.
#
# 📁 Proyecto: KarMind
# 🧩 Módulo: backend
# ✍️ Autor: Andrés Rivera Giraldo
# 🕒 Última actualización: 30/10/2025
# ===============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# ===============================================================
# 🔀 RUTAS PRINCIPALES
# ===============================================================
urlpatterns = [
    # -----------------------------------------------------------
    # 🎛️ Panel de Administración
    # -----------------------------------------------------------
    path('admin/', admin.site.urls),

    # -----------------------------------------------------------
    # 🧠 Núcleo del sistema (Aplicación 'core')
    # -----------------------------------------------------------
    path('', include('core.urls')),  # Incluye las rutas de la app 'core'
]


# ===============================================================
# 🗂️ CONFIGURACIÓN DE ARCHIVOS MEDIA (solo en desarrollo)
# ===============================================================
# Django no sirve archivos cargados por el usuario (MEDIA) por
# defecto. Este bloque los habilita únicamente cuando DEBUG = True.
#
# 📌 MEDIA_URL: URL base para acceder a los archivos (ej: /media/)
# 📌 MEDIA_ROOT: Ruta física donde se guardan (definida en settings.py)
#
# ⚠️ En producción, los archivos deben servirse desde el servidor
# web o un servicio CDN (S3, CloudFront, etc.).
# ===============================================================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
