from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Articulo, Origen
from simpex.models import Contenedor
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
