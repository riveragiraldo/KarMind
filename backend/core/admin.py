from django.contrib import admin
from .models import Departamento, Ciudad, Barrio, Empresa, Sede, Rol, User, Configuracion, Servicio, EstadoContacto, Contacto
from import_export import resources
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth import get_user_model
User = get_user_model()




# =====================================================
# 📘 Descripción general del archivo
# =====================================================
# Este módulo define la configuración del panel de administración de Django
# para los modelos del proyecto. Aquí se registran las entidades que podrán
# ser gestionadas desde la interfaz administrativa, junto con las opciones
# de visualización, filtrado y exportación de datos.
#
# El archivo utiliza la librería `django-import-export`, que facilita la 
# importación y exportación de información en diversos formatos (CSV, XLSX, JSON, etc.).
# 
# A medida que el sistema evolucione, este módulo puede ampliarse para incluir
# nuevos modelos y configuraciones administrativas según las necesidades del proyecto.


# =====================================================
# 🧩 Recursos para Import/Export: Departamentos
# =====================================================
class DepartamentosResources(resources.ModelResource):
    """
    Recurso que habilita la importación y exportación de datos 
    del modelo Departamento mediante la librería django-import-export.
    """
    class Meta:
        model = Departamento
        fields = ('id', 'nombre', 'is_active', 'fecha_creacion', 'fecha_actualizacion')
        # Si existen campos tipo ForeignKey a User, se pueden excluir:
        exclude = ('creado_por', 'actualizado_por')
        export_order = ('id', 'nombre', 'is_active', 'fecha_creacion', 'fecha_actualizacion')


# =====================================================
# 🗂️ Administración de Departamentos
# =====================================================
@admin.register(Departamento)
class DepartamentoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Configura la administración de los Departamentos en el panel de Django.
    Define los campos visibles y permite importar/exportar información.
    """
    list_display = ('id', 'nombre', 'is_active', 'fecha_creacion', 'fecha_actualizacion')
    resource_class = DepartamentosResources



# =====================================================
# 🧩 Recursos para Import/Export: Ciudades
# =====================================================
class CiudadesResources(resources.ModelResource):
    class Meta:
        model = Ciudad
        fields = ('id', 'nombre', 'departamento', 'is_active')
        exclude = ('creado_por', 'actualizado_por')
        export_order = ('id', 'nombre', 'departamento', 'is_active')


# =====================================================
# 🏙️ Administración de Ciudades
# =====================================================
@admin.register(Ciudad)
class CiudadAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Configura la administración de las Ciudades en el panel de Django.
    Define los campos mostrados y permite la gestión de relaciones con Departamentos.
    """
    list_display = ('id', 'nombre', 'departamento', 'is_active')
    resource_class = CiudadesResources


# =====================================================
# 🧩 Recursos para Import/Export: Barrios
# =====================================================
class BarriosResources(resources.ModelResource):
    class Meta:
        model = Barrio
        fields = ('id', 'nombre', 'ciudad', 'is_active')
        exclude = ('creado_por', 'actualizado_por')
        export_order = ('id', 'nombre', 'ciudad', 'is_active')


# =====================================================
# 🏘️ Administración de Barrios
# =====================================================
@admin.register(Barrio)
class BarrioAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Configura la administración de los Barrios en el panel de Django.
    Define la vista de lista, los campos visibles y las opciones 
    de importación/exportación de registros.
    """
    list_display = ('id', 'nombre', 'ciudad', 'is_active')
    resource_class = BarriosResources

# =====================================================
# 🏢 RECURSOS DE IMPORTACIÓN / EXPORTACIÓN
# =====================================================
class EmpresaResource(resources.ModelResource):
    class Meta:
        model = Empresa
        fields = (
            'id', 'identificacion', 'nombre', 'descripcion', 'eslogan',
            'direccion', 'ciudad__nombre', 'representante',
            'telefono', 'correo_electronico', 'is_active'
        )


class SedeResource(resources.ModelResource):
    class Meta:
        model = Sede
        fields = (
            'id', 'nombre', 'empresa__nombre', 'ciudad__nombre',
            'direccion', 'telefono', 'mail', 'is_active'
        )


class RolResource(resources.ModelResource):
    class Meta:
        model = Rol
        fields = ('id', 'nombre')


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'nombres', 'apellidos', 'telefono',
            'empresa__nombre', 'sede__nombre', 'rol__nombre',
            'is_active', 'is_staff', 'is_superuser'
        )


# =====================================================
# 🏢 ADMINISTRACIÓN DE EMPRESA
# =====================================================
@admin.register(Empresa)
class EmpresaAdmin(ImportExportModelAdmin):
    """
    Administra los registros de las empresas dentro del sistema KarMind.
    Permite importar/exportar datos y visualizar el logo en miniatura.
    """
    resource_class = EmpresaResource
    list_display = (
        'id', 'nombre', 'identificacion', 'ciudad', 'representante',
        'telefono', 'correo_electronico', 'is_active', 'ver_logo'
    )
    list_filter = ('ciudad', 'is_active')
    search_fields = ('nombre', 'identificacion', 'representante', 'correo_electronico')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    def ver_logo(self, obj):
        """
        Muestra una vista previa del logo en el panel de administración.
        """
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:8px;"/>', obj.logo.url)
        return "Sin logo"
    ver_logo.short_description = "Logo"


# =====================================================
# 🏬 ADMINISTRACIÓN DE SEDE
# =====================================================
@admin.register(Sede)
class SedeAdmin(ImportExportModelAdmin):
    """
    Administra las sedes asociadas a las empresas registradas.
    """
    resource_class = SedeResource
    list_display = ('id', 'nombre', 'empresa', 'ciudad', 'telefono', 'mail', 'is_active')
    list_filter = ('empresa', 'ciudad', 'is_active')
    search_fields = ('nombre', 'empresa__nombre', 'ciudad__nombre', 'telefono')
    ordering = ('empresa', 'nombre')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


# =====================================================
# 🧩 ADMINISTRACIÓN DE ROLES
# =====================================================
@admin.register(Rol)
class RolAdmin(ImportExportModelAdmin):
    """
    Gestiona los roles disponibles en el sistema KarMind.
    """
    resource_class = RolResource
    list_display = ('id', 'nombre')
    ordering = ('nombre',)
    search_fields = ('nombre',)


# =====================================================
# 👤 ADMINISTRACIÓN DE USUARIOS
# =====================================================
@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    """
    Administra los usuarios personalizados de KarMind, 
    con autenticación basada en correo electrónico y relaciones 
    a Empresa, Sede y Rol.
    """
    resource_class = UserResource
    list_display = (
        'id', 'email', 'nombres', 'apellidos', 'telefono',
        'empresa', 'sede', 'rol', 'is_active', 'is_staff'
    )
    list_filter = ('empresa', 'sede', 'rol', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombres', 'apellidos', 'telefono')
    ordering = ('nombres', 'apellidos')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ("Información Personal", {
            'fields': ('email', 'nombres', 'apellidos', 'telefono')
        }),
        ("Organización", {
            'fields': ('empresa', 'sede', 'rol')
        }),
        ("Credenciales y Permisos", {
            'fields': ('password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ("Fechas de Control", {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )


# =====================================================
# 🗂️ Administración de Configuración del Sistema KarMind
# =====================================================
# Este módulo define la interfaz administrativa del modelo
# Configuración, permitiendo gestionar parámetros globales,
# el documento PTDP, el logotipo institucional y el correo
# administrativo del sistema.
# =====================================================


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    """
    🎛️ Panel administrativo para el modelo Configuración.
    Permite administrar los parámetros principales del sistema,
    visualizar el logo y descargar el documento PTDP.
    """

    # ------------------------------------------------------
    # 📋 Listado principal
    # ------------------------------------------------------
    list_display = (
        'id',
        'periodo_pago',
        'periodo_revision',
        'email_administrativo',
        'ptdp_link',
        'logo_preview',
        'fecha_creacion',
        'fecha_actualizacion',
        'is_active',
    )

    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
        'logo_preview',
    )

    # ------------------------------------------------------
    # 🔗 Enlace de descarga para el documento PTDP
    # ------------------------------------------------------
    def ptdp_link(self, obj):
        """Muestra un enlace descargable con el nombre del archivo PTDP."""
        if obj.ptdp:
            return format_html('<a href="{}" download>{}</a>', obj.ptdp.url, obj.filename())
        return "Sin archivo"

    ptdp_link.short_description = "PTDP"

    # ------------------------------------------------------
    # 🖼️ Vista previa del logo institucional
    # ------------------------------------------------------
    def logo_preview(self, obj):
        """Muestra una vista previa del logotipo institucional."""
        if obj.logo:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:8px; border:1px solid #ccc;"/>',
                obj.logo.url
            )
        return "Sin logo"

    logo_preview.short_description = "Logo"

    # ------------------------------------------------------
    # 🧩 Estructura del formulario de edición
    # ------------------------------------------------------
    fieldsets = (
        ("Parámetros de configuración", {
            "fields": (
                "periodo_pago",
                "periodo_revision",
                "email_administrativo",
                "ptdp",
                "logo",
                "logo_preview",
            )
        }),
        ("Auditoría", {
            "fields": (
                "creado_por",
                "actualizado_por",
                "fecha_creacion",
                "fecha_actualizacion",
                "is_active",
            )
        }),
    )

    # ------------------------------------------------------
    # ⚙️ Configuración adicional
    # ------------------------------------------------------
    ordering = ('-fecha_creacion',)
    list_filter = ('is_active',)
    search_fields = ('email_administrativo', 'periodo_pago', 'periodo_revision')



# =====================================================
# 🗂️ Administración de Servicios
# =====================================================
# Configura la visualización del modelo Servicio dentro
# del panel administrativo de Django.
# =====================================================


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    """
    🎛️ Panel administrativo para la gestión de servicios.
    Permite visualizar y administrar los distintos servicios
    registrados en la plataforma.
    """

    list_display = (
        'id',
        'nombre',
        'is_active',
        'fecha_creacion',
        'fecha_actualizacion',
    )

    search_fields = ('nombre',)
    list_filter = ('is_active',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    # ----------------------------------------------------------
    # 📋 Organización de campos en el formulario de edición
    # ----------------------------------------------------------
    fieldsets = (
        ("Información del servicio", {
            "fields": ("nombre",)
        }),
        ("Auditoría", {
            "fields": (
                "creado_por",
                "actualizado_por",
                "fecha_creacion",
                "fecha_actualizacion",
                "is_active",
            )
        }),
    )

# =====================================================
# 🗂️ Administración de Estados de Servicio
# =====================================================
# Configura la visualización y gestión de los estados
# posibles en el panel administrativo de Django.
# =====================================================



@admin.register(EstadoContacto)
class EstadoContactoAdmin(admin.ModelAdmin):
    """
    🎛️ Panel administrativo para la gestión de estados de servicio.
    Permite crear, editar y visualizar los estados disponibles
    en el sistema KarMind.
    """

    list_display = ('id', 'nombre', 'color_hex', 'is_active', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('is_active',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ("Información del estado", {
            "fields": ("nombre", "descripcion", "color_hex", "is_active")
        }),
        ("Auditoría", {
            "fields": (
                "creado_por",
                "actualizado_por",
                "fecha_creacion",
                "fecha_actualizacion",
            )
        }),
    )


# =====================================================
# 🗂️ Administración: Contacto
# =====================================================
# Configuración del panel de administración para gestionar
# las solicitudes de contacto recibidas.
# =====================================================

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    """
    Panel administrativo para la gestión de Contactos.
    Permite visualizar datos clave, filtrar por estado/servicio
    y actualizar el registro (incluyendo asignar 'actualizado_por').
    """

    # Columnas en la vista de lista
    list_display = (
        'id',
        'nombres',
        'apellidos',
        'correo',
        'telefono',
        'servicio',
        'estado',
        'fecha_creacion',
        'is_active'
    )

    list_filter = ('estado', 'servicio', 'fecha_creacion', 'is_active')
    search_fields = ('nombres', 'apellidos', 'correo', 'telefono', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ("Información del remitente", {
            "fields": ("nombres", "apellidos", "correo", "telefono")
        }),
        ("Solicitud", {
            "fields": ("servicio", "descripcion", "acepta_politica", "estado")
        }),
        ("Auditoría", {
            "fields": ("actualizado_por", "fecha_creacion", "fecha_actualizacion", "is_active")
        }),
    )

    # Al guardar desde el admin, si se desea podemos automatizar que el usuario logueado
    # quede registrado en 'actualizado_por' (opcional). A continuación se implementa.
    def save_model(self, request, obj, form, change):
        """
        Sobrescribe el guardado para asignar 'actualizado_por' con el usuario actual del admin.
        """
        if request.user and request.user.is_authenticated:
            obj.actualizado_por = request.user
        super().save_model(request, obj, form, change)
