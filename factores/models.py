from django.db import models

# -----------------------------------------
#  TUS MODELOS EXISTENTES (opcional)
# -----------------------------------------
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


# -----------------------------------------
#  NUEVO MODELO PROFESIONAL Y ESCALABLE
# -----------------------------------------
class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)
    export_country = models.BooleanField(default=False)
    import_country = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.code} - {self.name}"


class CostType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TariffTable(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Tariff(models.Model):
    tariff_table = models.ForeignKey(TariffTable, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    cost_type = models.ForeignKey(CostType, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('tariff_table', 'country', 'cost_type')

    def __str__(self):
        return f"{self.tariff_table.name} | {self.country.code} | {self.cost_type.name}: {self.value}"
