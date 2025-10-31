from django.contrib import admin
from .models import Departamento, Ciudad, Barrio, Empresa, Sede, Rol, User, Configuracion
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
# Configuración, permitiendo la gestión de parámetros globales
# del sistema, la carga del documento PTDP y del logotipo institucional.
# =====================================================

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    """
    🎛️ Panel administrativo para el modelo Configuración.
    Permite gestionar los parámetros principales del sistema,
    el documento PTDP y el logotipo institucional.
    """

    # ------------------------------------------------------
    # 📋 Listado principal
    # ------------------------------------------------------
    list_display = (
        'id',
        'periodo_pago',
        'periodo_revision',
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
        """
        Muestra un enlace descargable con el nombre del archivo PTDP.
        Si no existe archivo, muestra 'Sin archivo'.
        """
        if obj.ptdp:
            return format_html(
                '<a href="{}" download>{}</a>',
                obj.ptdp.url,
                obj.filename()
            )
        return "Sin archivo"

    ptdp_link.short_description = "PTDP"

    # ------------------------------------------------------
    # 🖼️ Vista previa del logo institucional
    # ------------------------------------------------------
    def logo_preview(self, obj):
        """
        Muestra una vista previa del logotipo institucional en miniatura.
        Si no hay logo cargado, muestra 'Sin logo'.
        """
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
    search_fields = ('periodo_pago', 'periodo_revision')
