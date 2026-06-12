from django.contrib import admin
from .models import Usuarios, Ratas, Cajas, Bitacora, Anestesicos, Tejidos, Condiciones, Roles, PesoSemanal, Ubicaciones
# Register your models here.

@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('idusuario', 'nombreusuario', 'apellidopaterno', 'apellidomaterno', 'sexo', 'idrol')
    search_fields = ('nombreusuario', 'apellidopaterno', 'apellidomaterno')
    list_filter = ('sexo', 'idrol')
    ordering = ('idusuario',)


@admin.register(Ratas)
class RatasAdmin(admin.ModelAdmin):
    list_display = ('idrata', 'fechacirugia', 'numerocola', 'idcondicion')
    search_fields = ('idrata', 'idcondicion__nombrecondicion')
    list_filter = ('idcondicion',)
    ordering = ('idrata',)


@admin.register(Cajas)
class CajasAdmin(admin.ModelAdmin):
    list_display = ('idcaja', 'cantidadratas', 'sexo', 'fechanacimiento', 'idusuario', 'talla')
    search_fields = ('idusuario__nombreusuario',)
    list_filter = ('sexo', 'idusuario')
    ordering = ('idcaja',)


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('idbitacora', 'idrata', 'idusuario', 'fechacirujia', 'dosis', 'dosistotal', 'idanestesico')
    search_fields = ('idrata__idrata', 'idusuario__nombreusuario', 'idanestesico__nombreanestesico')
    list_filter = ('idusuario', 'idanestesico')
    ordering = ('idbitacora',)


@admin.register(Anestesicos)
class AnestesicosAdmin(admin.ModelAdmin):
    list_display = ('idanestesico', 'nombreanestesico', 'descripcion')
    search_fields = ('nombreanestesico',)
    ordering = ('idanestesico',)


@admin.register(Tejidos)
class TejidosAdmin(admin.ModelAdmin):
    list_display = ('idtejido', 'nombretejido', 'descripcion')
    search_fields = ('nombretejido',)
    ordering = ('idtejido',)


@admin.register(Condiciones)
class CondicionesAdmin(admin.ModelAdmin):
    list_display = ('idcondicion', 'nombrecondicion', 'descripcion')
    search_fields = ('nombrecondicion',)
    ordering = ('idcondicion',)

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('idrol', 'nombrerol', 'descripcion')
    search_fields = ('nombrerol',)
    ordering = ('idrol',)

@admin.register(Ubicaciones)
class UbicacionesAdmin(admin.ModelAdmin):
    list_display  = ('idubicacion', 'nombreubicacion', 'descripcion')
    search_fields = ('nombreubicacion',)
    ordering      = ('idubicacion',)