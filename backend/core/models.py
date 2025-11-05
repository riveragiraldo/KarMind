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
from django.core.validators import RegexValidator, MaxLengthValidator
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
# Este modelo almacena los parámetros generales del sistema,
# como los períodos de pago y revisión, el documento PTDP en PDF
# y el logotipo institucional. 
# 
# Hereda los campos definidos en BaseModel:
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
    Valida que el archivo PDF no supere los 5 MB.
    """
    max_size = 5 * 1024 * 1024  # 5 MB
    if archivo.size > max_size:
        raise ValidationError("El archivo no debe superar los 5 MB.")


def validar_pdf(archivo):
    """
    Valida que el archivo tenga una extensión .pdf (no sensible a mayúsculas).
    """
    if not archivo.name.lower().endswith('.pdf'):
        raise ValidationError("Solo se permiten archivos con formato PDF.")


def validar_tamano_imagen(archivo):
    """
    Valida que el tamaño del archivo de imagen no supere los 5 MB.
    """
    max_size = 5 * 1024 * 1024  # 5 MB
    if archivo.size > max_size:
        raise ValidationError("El logo no debe superar los 5 MB.")


def validar_logo_png(archivo):
    """
    Valida que el logo sea un archivo PNG cuadrado y válido.
    """
    if not archivo.name.lower().endswith('.png'):
        raise ValidationError("El logo debe estar en formato PNG.")

    try:
        imagen = Image.open(archivo)
        if imagen.format != 'PNG':
            raise ValidationError("El archivo debe ser una imagen PNG válida.")
        if imagen.width != imagen.height:
            raise ValidationError("El logo debe tener proporciones cuadradas (ancho = alto).")
    except Exception:
        raise ValidationError("El archivo no es una imagen válida o está dañado.")


def ptdp_upload_path(instance, filename):
    """
    Define la ruta y el formato de nombre para el documento PTDP cargado.
    El archivo se almacenará con el formato:
    configuracion/PTDP_ddmmaaaahhmmss.pdf
    """
    timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
    filename = f"PTDP_{timestamp}.pdf"
    return os.path.join("configuracion", filename)


def logo_upload_path(instance, filename):
    """
    Define la ruta y el nombre fijo para el logotipo institucional.
    Siempre se almacenará como: configuracion/logo.png
    """
    return os.path.join("configuracion", "logo.png")


# --------------------------------------------------------------
# 🧱 MODELO: Configuración
# --------------------------------------------------------------
class Configuracion(BaseModel):
    """
    Representa los parámetros de configuración global del sistema KarMind.

    Este modelo centraliza la gestión de información operativa y visual
    del sistema, permitiendo ajustar períodos administrativos y mantener
    recursos institucionales como el documento PTDP y el logotipo.
    """

    # ----------------------------------------------------------
    # 🔹 Campos de Configuración Operativa
    # ----------------------------------------------------------
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

    # ----------------------------------------------------------
    # 📄 Documento PTDP (PDF)
    # ----------------------------------------------------------
    ptdp = models.FileField(
        "PTDP (Documento PDF)",
        upload_to=ptdp_upload_path,
        validators=[validar_pdf, validar_tamano_pdf],
        null=True,
        blank=True,
        help_text="Archivo PDF máximo de 5 MB."
    )

    # ----------------------------------------------------------
    # 🖼️ Logotipo Institucional (PNG)
    # ----------------------------------------------------------
    logo = models.ImageField(
        "Logo Institucional",
        upload_to=logo_upload_path,
        validators=[validar_logo_png, validar_tamano_imagen],
        null=True,
        blank=True,
        help_text="Archivo PNG cuadrado de máximo 5 MB. Se almacenará como 'logo.png'."
    )

    # ----------------------------------------------------------
    # ⚙️ Configuración del Modelo
    # ----------------------------------------------------------
    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"
        ordering = ['-fecha_creacion']

    # ----------------------------------------------------------
    # 📘 Representación Legible
    # ----------------------------------------------------------
    def __str__(self):
        """
        Devuelve una representación textual legible de la configuración.
        """
        return f"Configuración (Pago: {self.periodo_pago} / Revisión: {self.periodo_revision})"

    # ----------------------------------------------------------
    # 📂 Métodos Utilitarios
    # ----------------------------------------------------------
    def filename(self):
        """
        Retorna el nombre del archivo PTDP, si existe.
        """
        return os.path.basename(self.ptdp.name) if self.ptdp else None

    def logo_filename(self):
        """
        Retorna el nombre del archivo de logotipo, si existe.
        """
        return os.path.basename(self.logo.name) if self.logo else None

# ==============================================================
# 📦 MODELO: Servicio
# ==============================================================
# Este modelo representa los distintos tipos de servicios que 
# KarMind ofrece. Cada servicio tiene un nombre único, con una 
# longitud máxima de 25 caracteres. Hereda de BaseModel para 
# conservar trazabilidad (fechas, usuarios y estado activo).
# ==============================================================


# --------------------------------------------------------------
# 🧱 MODELO: Servicio
# --------------------------------------------------------------
class Servicio(BaseModel):
    """
    Define los servicios que ofrece la plataforma KarMind.
    Cada registro corresponde a un tipo de servicio único.
    """

    nombre = models.CharField(
        "Nombre del servicio",
        max_length=25,
        unique=True,
        help_text="Nombre corto y descriptivo del servicio (máx. 25 caracteres)."
    )

    # ----------------------------------------------------------
    # 🔧 CONFIGURACIÓN DEL MODELO
    # ----------------------------------------------------------
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']

    # ----------------------------------------------------------
    # 📘 REPRESENTACIÓN LEGIBLE
    # ----------------------------------------------------------
    def __str__(self):
        """
        Retorna una representación legible del servicio.
        """
        return self.nombre
# ==============================================================
# 📦 MODELO: EstadoServicio
# ==============================================================
# Este modelo define los diferentes estados posibles que puede
# tener una solicitud o servicio dentro del sistema KarMind.
# Permite gestionar dinámicamente los estados desde el panel
# administrativo sin requerir cambios en el código fuente.
# ==============================================================


# --------------------------------------------------------------
# 🧱 MODELO: EstadoServicio
# --------------------------------------------------------------
class EstadoContacto(BaseModel):
    """
    Representa un estado que puede asignarse a un servicio o
    solicitud de contacto (por ejemplo: Pendiente, En proceso, Respondido).
    """

    nombre = models.CharField(
        "Nombre del estado",
        max_length=30,
        unique=True,
        help_text="Nombre del estado (por ejemplo: Pendiente, En proceso, Respondido)."
    )

    descripcion = models.TextField(
        "Descripción",
        blank=True,
        help_text="Descripción opcional del propósito o uso de este estado."
    )

    color_hex = models.CharField(
        "Color representativo (HEX)",
        max_length=7,
        default="#6c757d",
        help_text="Color representativo en formato HEX (ejemplo: #28a745 para verde)."
    )

    # ----------------------------------------------------------
    # 🔧 CONFIGURACIÓN DEL MODELO
    # ----------------------------------------------------------
    class Meta:
        verbose_name = "Estado de Contacto"
        verbose_name_plural = "Estados de Contacto"
        ordering = ['nombre']

    # ----------------------------------------------------------
    # 📘 REPRESENTACIÓN LEGIBLE
    # ----------------------------------------------------------
    def __str__(self):
        """
        Retorna una representación legible del estado.
        """
        return self.nombre
    

# ==============================================================
# 📦 MODELO: Contacto
# ==============================================================
# Este modelo almacena las solicitudes o mensajes enviados por
# clientes/visitantes a través del formulario público.
#
# Características principales:
# - No requiere usuario autenticado para su creación.
# - Registra fecha de creación y actualización.
# - Registra el usuario que realizó la última modificación
#   (campo 'actualizado_por') para auditoría administrativa.
# - Relaciona la solicitud con un Servicio y con un EstadoContacto.
# - Valida consentimiento explícito de tratamiento de datos.
# ==============================================================


class Contacto(models.Model):
    """
    Representa una solicitud de contacto enviada desde el formulario público.

    Campos:
        fecha_creacion: Fecha y hora en que se creó la solicitud (auto).
        nombres: Nombres del remitente (obligatorio, max 20).
        apellidos: Apellidos del remitente (opcional, max 20).
        telefono: Teléfono de contacto (obligatorio, validado).
        correo: Correo electrónico del remitente (obligatorio).
        servicio: FK a Servicio (obligatorio).
        descripcion: Descripción de la solicitud (obligatorio, max 200).
        acepta_politica: Bool indicando consentimiento (obligatorio, debe ser True).
        estado: FK a EstadoContacto (obligatorio, si no se provee se intenta asignar 'PENDIENTE').
        actualizado_por: Usuario que realizó la última modificación desde admin (nullable).
        fecha_actualizacion: Fecha de la última modificación (auto).
    """

    # -----------------------------
    # Campos principales
    # -----------------------------
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se recibió la solicitud."
    )

    nombres = models.CharField(
        "Nombres",
        max_length=20,
        validators=[MaxLengthValidator(20)],
        help_text="Nombres del remitente (máx. 20 caracteres)."
    )

    apellidos = models.CharField(
        "Apellidos",
        max_length=20,
        blank=True,
        validators=[MaxLengthValidator(20)],
        help_text="Apellidos del remitente (opcional, máx. 20 caracteres)."
    )

    telefono = models.CharField(
        "Teléfono",
        max_length=16,
        validators=[
            RegexValidator(r'^\+?\d{7,15}$',
                           message="El teléfono debe contener entre 7 y 15 dígitos y puede incluir '+' para código país.")
        ],
        help_text="Número telefónico del remitente (incluya código país si aplica)."
    )

    correo = models.EmailField(
        "Correo electrónico",
        help_text="Correo electrónico de contacto del remitente."
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='contactos',
        verbose_name="Servicio solicitado",
        help_text="Servicio sobre el cual se solicita información."
    )

    descripcion = models.CharField(
        "Descripción de la solicitud",
        max_length=200,
        validators=[MaxLengthValidator(200)],
        help_text="Detalle o descripción de la solicitud (máx. 200 caracteres)."
    )

    acepta_politica = models.BooleanField(
        "Acepta política de tratamiento de datos",
        default=False,
        help_text="El usuario debe aceptar la política de tratamiento de datos para enviar la solicitud."
    )

    estado = models.ForeignKey(
        EstadoContacto,
        on_delete=models.PROTECT,
        related_name='contactos',
        null=True,
        blank=True,
        verbose_name="Estado de la solicitud",
        help_text="Estado actual de la solicitud. Si no se especifica, se intentará asignar 'PENDIENTE'."
    )

    # -----------------------------
    # Auditoría de modificaciones (no requerido para creación)
    # -----------------------------
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contactos_actualizados',
        verbose_name="Usuario que modificó",
        help_text="Usuario del sistema que realizó la última modificación."
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última modificación del registro."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la solicitud está activa o fue archivada/eliminada lógicamente."
    )

    # -----------------------------
    # Metadatos del modelo
    # -----------------------------
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['correo']),
            models.Index(fields=['telefono']),
            models.Index(fields=['estado']),
        ]

    # -----------------------------
    # Representación legible
    # -----------------------------
    def __str__(self):
        servicio_nombre = self.servicio.nombre if self.servicio else "—"
        return f"{self.nombres} {self.apellidos or ''}".strip() + f" — {servicio_nombre}"

    # -----------------------------
    # Validación de modelo (se ejecuta en full_clean())
    # -----------------------------
    def clean(self):
        """
        Realiza validaciones lógicas del modelo:
        - Asegura que el consentimiento (acepta_politica) sea True.
        - Si no se especificó estado, intenta asignar el EstadoContacto 'PENDIENTE'.
        - Si no existe 'PENDIENTE', se lanza ValidationError indicando crear el estado.
        """
        errors = {}

        # 1) Consentimiento obligatorio
        if not self.acepta_politica:
            errors['acepta_politica'] = ValidationError(
                "El envío requiere la aceptación de la política de tratamiento de datos."
            )

        # 2) Estado: si no hay estado asignado, intentar obtener el estado 'PENDIENTE'
        if not self.estado:
            try:
                pendiente = EstadoContacto.objects.filter(nombre__iexact='PENDIENTE').first()
                if pendiente:
                    self.estado = pendiente
                else:
                    errors['estado'] = ValidationError(
                        "No existe un estado 'PENDIENTE'. Por favor cree un EstadoContacto con nombre 'PENDIENTE'."
                    )
            except Exception as e:
                # Si falla la consulta (p. ej., migraciones), añadimos error genérico
                errors['estado'] = ValidationError(
                    "No fue posible asignar el estado por defecto. Verifique que el modelo EstadoContacto exista."
                )

        if errors:
            raise ValidationError(errors)

    # -----------------------------
    # Save: asegurar la validación y comportamiento por defecto
    # -----------------------------
    def save(self, *args, **kwargs):
        """
        Antes de guardar:
        - Ejecuta clean() para garantizar integridad (consentimiento y estado).
        - Actualiza 'fecha_actualizacion' automáticamente (gestión de Django).
        """
        # Intentar validación completa del objeto
        self.full_clean()
        super().save(*args, **kwargs)

