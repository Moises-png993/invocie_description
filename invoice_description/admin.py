from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Articulo, Origen
from simpex.models import Contenedor
from factores.models import Flete, Unidades, CostoPais

admin.site.site_header = "Impex Administration"  
admin.site.site_title = "Impex Admin Portal"      
admin.site.index_title = "Impex Administration"  
admin.site.site_url = "/app/home"  

@admin.register(Articulo)
class ArticuloAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(Origen)
class OringenAdmin(ImportExportModelAdmin):
    list_display = ('codigo', 'origen')
    search_fields = ('codigo', 'origen')

@admin.register(Contenedor)
class ContenedorAdmin(ImportExportModelAdmin):
    list_display = (
        'pais', 'embarque', 'expediente', 'tamano',
        'fecha_pos', 'fecha_despacho', 'status',
        'transporte', 'eta', 'dai', 'fts'
    )
    list_filter = ('pais', 'status', 'transporte')
    search_fields = ('embarque', 'expediente', 'pais', 'transporte')

@admin.register(Flete)
class ContenedorAdmin(ImportExportModelAdmin):
    list_display = (
        'pais', 'flete_ipl', 'flete_blue', 'flete_directo',
    )
    list_filter = ('pais', 'flete_ipl', 'flete_blue', 'flete_directo')
    search_fields = ('pais', 'flete_ipl', 'flete_blue', 'flete_directo')

@admin.register(Unidades)
class ContenedorAdmin(ImportExportModelAdmin):
    list_display = (
        'grupo_articulo', 'unidades_contenedor', 'unidades_cbm'
    )
    list_filter = ('grupo_articulo', 'unidades_contenedor', 'unidades_cbm')
    search_fields = ('grupo_articulo', 'unidades_contenedor', 'unidades_cbm')

@admin.register(CostoPais)
class CostoPaisAdmin(ImportExportModelAdmin):
    list_display = (
        'pais',
        'almacenaje',
        'honorarios_aduanales',
        'inspeccion_no_intrusiva',
        'custodio',
        'otros_gastos',
        'flete_terrestre_ca',
        'flete_local',
    )
    list_filter = ('pais',)
    search_fields = ('pais',)