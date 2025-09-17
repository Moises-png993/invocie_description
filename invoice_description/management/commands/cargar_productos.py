import csv
from django.core.management.base import BaseCommand
from invoice_description.models import Articulo  # 👈 usa tu modelo real

class Command(BaseCommand):
    help = 'Carga artículos desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('archivo_csv', type=str, help='Ruta al archivo CSV con artículos')

    def handle(self, *args, **kwargs):
        archivo_csv = kwargs['archivo_csv']

        with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile,delimiter=';')  # 👈 usamos csv.reader, no DictReader
            articulos = []

            for row in reader:
                if len(row) < 2:
                    continue  # saltar filas inválidas
                codigo, descripcion = row[0], row[1]
                articulos.append(
                    Articulo(codigo=codigo.strip(), descripcion=descripcion.strip())
                )

            Articulo.objects.bulk_create(articulos, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Se cargaron {len(articulos)} artículos'))

