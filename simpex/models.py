from django.db import models

class Contenedor(models.Model):
    pais = models.CharField(max_length=100)
    embarque = models.CharField(max_length=100)
    expediente = models.CharField(max_length=50, unique=True)
    tamano = models.CharField(max_length=20)  # Ej: "20 ft", "40 ft"
    fecha_pos = models.DateField(null=True, blank=True)
    fecha_despacho = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ("EN_TRANSITO", "En tránsito"),
        ("VERIFICADO", "Verificado"),
        ("ENTREGADO", "Entregado"),
    ])
    transporte = models.CharField(max_length=50)  # Ej: "MSC", "Maersk"
    eta = models.DateField(null=True, blank=True)
    dai = models.CharField(max_length=40)
    fts = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.embarque} - {self.expediente}"

