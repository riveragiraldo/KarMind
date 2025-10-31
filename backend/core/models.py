"""
=======================================================
📁 MODELS.PY — Definición de estructuras de datos del sistema KarMind
=======================================================

Este módulo agrupa los modelos de datos principales utilizados por la 
aplicación KarMind. Su objetivo es definir estructuras coherentes y 
escalables para representar las entidades y relaciones del sistema, 
siguiendo estándares de diseño orientados a la trazabilidad, consistencia 
y reutilización del código.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from PIL import Image
from django.utils import timezone
import os
from datetime import datetime


# =====================================================
# 🧩 Modelo Base: Campos heredados comunes
# =====================================================
class BaseModel(models.Model):
    """
    Modelo abstracto que define campos comunes para trazabilidad de datos.
    Incluye registro de usuario creador, actualizador, fechas y estado activo.
    """

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_creado_por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        help_text="Usuario que creó el registro originalmente."
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_actualizado_por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        help_text="Último usuario que modificó el registro."
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Registro creado por {self.creado_por} el {self.fecha_creacion}"


# =====================================================
# 🌎 Modelo: Departamento
# =====================================================
class Departamento(BaseModel):
    nombre = models.CharField(max_length=70, unique=True)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# =====================================================
# 🏙️ Modelo: Ciudad
# =====================================================
class Ciudad(BaseModel):
    nombre = models.CharField(max_length=50)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='ciudades'
    )

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        unique_together = ('nombre', 'departamento')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"


# =====================================================
# 🏘️ Modelo: Barrio
# =====================================================
class Barrio(BaseModel):
    nombre = models.CharField(max_length=100)
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.CASCADE,
        related_name='barrios'
    )

    class Meta:
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"
        unique_together = ('nombre', 'ciudad')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.ciudad.nombre}"


# =====================================================
# 🏢 Modelo: Empresa
# =====================================================
def validar_logo_cuadrado(logo):
    try:
        with Image.open(logo) as img:
            if img.width != img.height:
                raise ValidationError("El logo debe tener proporciones cuadradas (ancho = alto).")
    except Exception:
        raise ValidationError("El archivo proporcionado no es una imagen válida.")


def validar_tamano_logo(logo):
    limite_mb = 5
    if logo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"El tamaño máximo permitido del logo es de {limite_mb} MB.")


class Empresa(BaseModel):
    identificacion = models.BigIntegerField(unique=True)
    nombre = models.CharField(max_length=30, unique=True)
    logo = models.ImageField(
        upload_to='empresas/logos/',
        validators=[validar_logo_cuadrado, validar_tamano_logo]
    )
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    eslogan = models.CharField(max_length=40, blank=True, null=True)
    direccion = models.CharField(max_length=40)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='empresas')
    representante = models.CharField(max_length=30)
    telefono = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{7,12}$', message="El teléfono debe contener entre 7 y 12 dígitos.")]
    )
    correo_electronico = models.EmailField()

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.ciudad.nombre})"


# =====================================================
# 🏬 Modelo: Sede
# =====================================================
class Sede(BaseModel):
    nombre = models.CharField(max_length=255)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE)
    ciudad = models.ForeignKey('Ciudad', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    mail = models.EmailField(blank=True, null=True)

    class Meta:
        unique_together = ('empresa', 'ciudad', 'nombre')
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre} ({self.ciudad.nombre})"


# =====================================================
# 🧠 MODELOS DE USUARIO Y ROLES
# =====================================================
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
)
from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _


# =====================================================
# ⚙️ GESTOR PERSONALIZADO DE USUARIOS
# =====================================================
class UserManager(BaseUserManager):
    def create_user(self, email, nombres, apellidos, telefono, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio para crear un usuario.')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            telefono=telefono,
            **extra_fields
        )
        user.set_password(password)
        if not user.username:
            ultimo_id = self.model.objects.count() + 1
            user.username = f"user_{ultimo_id:03d}"
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombres, apellidos, telefono, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('El superusuario debe tener is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, nombres, apellidos, telefono, password, **extra_fields)


# =====================================================
# 🧩 MODELO: Rol
# =====================================================
class Rol(models.Model):
    ROL_CHOICES = [
        ('SUPERUSUARIO', 'Superusuario'),
        ('EMPRESA', 'Empresa'),
    ]
    nombre = models.CharField(max_length=20, choices=ROL_CHOICES, unique=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# =====================================================
# 👤 MODELO: Usuario Personalizado
# =====================================================
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    telefono = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{7,12}$', message="El teléfono debe contener entre 7 y 12 dígitos.")]
    )

    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'telefono']

    objects = UserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['nombres', 'apellidos']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.email})"

    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


# ==============================================================
# 📦 MODELO: Configuración del Sistema KarMind
# ==============================================================
# Este modelo permite almacenar parámetros generales del sistema,
# como los períodos de pago y revisión, y el archivo PTDP (PDF).
# Hereda los campos comunes definidos en BaseModel:
# - fecha_creacion
# - fecha_actualizacion
# - is_active
# - creado_por
# - actualizado_por
# ==============================================================


# --------------------------------------------------------------
# 🧰 VALIDADORES PERSONALIZADOS
# --------------------------------------------------------------
def validar_tamano_pdf(archivo):
    """
    Valida que el tamaño del archivo no supere los 5 MB.
    """
    max_size = 5 * 1024 * 1024  # 5 MB
    if archivo.size > max_size:
        raise ValidationError("El archivo no debe superar los 5 MB.")


def validar_pdf(archivo):
    """
    Valida que el archivo tenga extensión .pdf (no sensible a mayúsculas).
    """
    if not archivo.name.lower().endswith('.pdf'):
        raise ValidationError("Solo se permiten archivos con formato PDF.")

def ptdp_upload_path(instance, filename):
    """
    📁 Define la ruta y formato del nombre del archivo PDF cargado.
    El archivo se guardará con el formato:
    PTDP_ddmmaaaahhmmss.pdf
    """
    timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
    filename = f"PTDP_{timestamp}.pdf"
    return os.path.join("configuracion", filename)


# --------------------------------------------------------------
# 🧱 MODELO: Configuración
# --------------------------------------------------------------
class Configuracion(BaseModel):
    """
    Representa los parámetros de configuración global del sistema KarMind.

    Este modelo se utilizará para definir valores operativos
    y administrativos que pueden modificarse desde el panel de control
    (por ejemplo: períodos de pago, revisión, documentos base, etc.).
    """

    periodo_pago = models.PositiveIntegerField(
        "Período de Pago (días)",
        default=0,
        help_text="Valor entero positivo (incluye 0) que define el período de pago en días."
    )

    periodo_revision = models.PositiveIntegerField(
        "Período de Revisión (días)",
        default=0,
        help_text="Valor entero positivo (incluye 0) que define el período de revisión en días."
    )

    ptdp = models.FileField(
        "PTDP (Documento PDF)",
        upload_to=ptdp_upload_path,
        validators=[validar_pdf, validar_tamano_pdf],
        null=True,
        blank=True,
        help_text="Archivo PDF máximo de 5 MB."
    )

    # ----------------------------------------------------------
    # 🔧 CONFIGURACIÓN DEL MODELO
    # ----------------------------------------------------------
    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"
        ordering = ['-fecha_creacion']

    # ----------------------------------------------------------
    # 📘 REPRESENTACIÓN LEGIBLE
    # ----------------------------------------------------------
    def __str__(self):
        """
        Retorna una representación legible de la configuración actual.
        """
        return f"Configuración (Pago: {self.periodo_pago} / Revisión: {self.periodo_revision})"
    def filename(self):
        """Retorna solo el nombre del archivo PTDP."""
        return os.path.basename(self.ptdp.name)

