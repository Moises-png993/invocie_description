from django.db import models
from django.db.models import F
from django.db.models.functions import Round

# ---------------------------
#  MODELO DE FLETE
# ---------------------------

class FleteQuerySet(models.QuerySet):
    def with_costos(self, unidades_contenedor):
        """
        Agrega columnas calculadas al queryset para cada tipo de flete.
        Se puede usar así:
        Flete.objects.with_costos(1000)
        """
        return self.annotate(
            costo_unitario_ipl=Round(F('flete_ipl') / unidades_contenedor, 2),
            costo_unitario_blue=Round(F('flete_blue') / unidades_contenedor, 2),
            costo_unitario_directo=Round(F('flete_directo') / unidades_contenedor, 2),
        )
# ---------------------------
#  MODELO DE UNIDADES
# ---------------------------

class Unidades(models.Model):
    grupo_articulo = models.CharField(max_length=50, unique=True)
    unidades_contenedor = models.PositiveIntegerField()
    unidades_cbm = models.PositiveIntegerField()

    def __str__(self):
        return self.grupo_articulo

class Flete(models.Model):
    pais = models.CharField(max_length=100, unique=True)
    flete_ipl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    flete_blue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    flete_directo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Activamos el QuerySet personalizado
    objects = FleteQuerySet.as_manager()

    def __str__(self):
        return self.pais

    # ---------------------------
    #  MÉTODOS DE CÁLCULO
    # ---------------------------

    def costo_unitario_ipl(self, unidades_contenedor):
        """Devuelve el costo por unidad para flete_ipl."""
        if unidades_contenedor:
            return round(float(self.flete_ipl or 0) / unidades_contenedor, 2)
        return None

    def costo_unitario_blue(self, unidades_contenedor):
        """Devuelve el costo por unidad para flete_blue."""
        if unidades_contenedor:
            return round(float(self.flete_blue or 0) / unidades_contenedor, 2)
        return None

    def costo_unitario_directo(self, unidades_contenedor):
        """Devuelve el costo por unidad para flete_directo."""
        if unidades_contenedor:
            return round(float(self.flete_directo or 0) / unidades_contenedor, 2)
        return None



