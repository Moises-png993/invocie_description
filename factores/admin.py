from django.contrib import admin
from django.contrib.admin import AdminSite
from factores.models import Flete, Unidades, Tariff, Country, CostType, TariffTable
from import_export.admin import ImportExportModelAdmin

# ========== CONFIGURACIÓN DEL ADMIN ESTÁNDAR (default) ==========
admin.site.site_header = "Impex - Administration"  
admin.site.site_title = "Impex Admin Portal 2"      
admin.site.index_title = "Impex Administration 2"  
admin.site.site_url = "/app/home"  

# --- ModelAdmin para el admin estándar
class FleteAdmin(ImportExportModelAdmin):
    list_display = ('pais', 'flete_ipl', 'flete_blue', 'flete_directo', 'flete_luno')
    list_filter = ('pais', 'flete_ipl', 'flete_blue', 'flete_directo', 'flete_luno')
    search_fields = ('pais', 'flete_ipl', 'flete_blue', 'flete_directo', 'flete_luno')

class UnidadesAdmin(ImportExportModelAdmin):
    list_display = ('grupo_articulo', 'unidades_contenedor', 'unidades_cbm')
    list_filter = ('grupo_articulo', 'unidades_contenedor', 'unidades_cbm')
    search_fields = ('grupo_articulo', 'unidades_contenedor', 'unidades_cbm')

class CountryAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_filter = ('code', 'name')
    search_fields = ('code', 'name')

class CostTypeAdmin(ImportExportModelAdmin):
    """CostType - Solo lectura. Editable solo desde Tariff."""
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    # Hacer solo lectura
    readonly_fields = ('name',)
    
    def has_add_permission(self, request):
        """No permitir crear nuevos CostType desde este admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar CostType desde este admin"""
        return False

class TariffTableAdmin(ImportExportModelAdmin):
    """TariffTable - Solo lectura. Editable solo desde Tariff."""
    list_display = ('name', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    # Hacer solo lectura
    readonly_fields = ('name', 'description')
    
    def has_add_permission(self, request):
        """No permitir crear nuevas TariffTable desde este admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar TariffTable desde este admin"""
        return False

class TariffAdmin(ImportExportModelAdmin):
    list_display = ('tariff_table', 'country', 'cost_type', 'value')
    list_filter = ('tariff_table', 'country', 'cost_type')
    search_fields = ('tariff_table__name', 'country__code', 'country__name', 'cost_type__name')
    ordering = ('country__code', 'cost_type__name')

# Registrar en el admin estándar (default)
# Nota: CostType y TariffTable NO se registran aquí (solo editables desde Tariff)
admin.site.register(Flete, FleteAdmin)
admin.site.register(Unidades, UnidadesAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Tariff, TariffAdmin)



# ========== SEGUNDO PANEL ADMIN (admin interno) ==========
class AdminInterno(AdminSite):
    site_header = "Impex - Panel Interno"
    site_title = "Admin Interno"
    index_title = "Administración Interna"

    def has_permission(self, request):
        """Controlar acceso: superusers o usuarios staff del grupo 'interno'"""
        user = request.user
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        try:
            return user.is_staff and user.groups.filter(name='interno').exists()
        except Exception:
            return user.is_staff


# Crear la instancia para usar en urls.py
admin_interno = AdminInterno(name='admin_interno')

# Registrar los mismos modelos pero reutilizando las clases ya definidas
# Nota: CostType y TariffTable NO se registran aquí (solo editables desde Tariff)
admin_interno.register(Flete, FleteAdmin)
admin_interno.register(Unidades, UnidadesAdmin)
admin_interno.register(Country, CountryAdmin)
admin_interno.register(Tariff, TariffAdmin)
