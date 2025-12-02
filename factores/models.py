from django.db import models
from django.db.models import F
from django.db.models.functions import Round


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
    flete_luno = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class CostoPais(models.Model):
    PAISES = [
        ('SV', 'El Salvador'),
        ('GT', 'Guatemala'),
        ('HN', 'Honduras'),
        ('CR', 'Costa Rica'),
        ('PA', 'Panamá'),
        ('NI', 'Nicaragua'),
    ]

    pais = models.CharField(max_length=2, choices=PAISES, unique=True)

    almacenaje = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    honorarios_aduanales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inspeccion_no_intrusiva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custodio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    otros_gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    flete_terrestre_ca = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    flete_local = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return dict(self.PAISES).get(self.pais, self.pais)



