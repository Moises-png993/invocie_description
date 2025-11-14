# invoice_description/models.py
from django.db import models

class Articulo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
class Origen(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    origen = models.TextField()

    def __str__(self):
        return f"{self.codigo} - {self.origen}"