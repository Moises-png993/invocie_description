import pandas as pd
from django.shortcuts import render
from .forms import ExcelUploadForm
from .models import Flete, Unidades

def upload_excel(request):
    df_resultado = None

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['file']

            # Leer el Excel con pandas
            df = pd.read_excel(excel_file)

            # Normalizar columnas
            df.columns = [col.strip().upper() for col in df.columns]

            # Procesar: traer flete desde BD según país
            resultados = []
            for _, row in df.iterrows():
                pais = row.get('PAIS ORIGEN')
                grupo = row.get('GRUPO ARTICULOS')
                fob = row.get('FOB')

                try:
                    flete = Flete.objects.get(pais__iexact=pais)
                    unidades = Unidades.objects.get(grupo_articulo__iexact=grupo)
                    costo_unitario = round(float(flete.flete_ipl or 0) / unidades.unidades_contenedor, 2)
                    costo_total = round(costo_unitario + float(fob or 0), 2)
                except (Flete.DoesNotExist, Unidades.DoesNotExist):
                    costo_unitario = None
                    costo_total = None

                resultados.append({
                    'PAIS ORIGEN': pais,
                    'GRUPO ARTICULOS': grupo,
                    'FOB': fob,
                    'FLETE IPL': flete.flete_ipl if 'flete' in locals() else None,
                    'COSTO UNITARIO': costo_unitario,
                    'COSTO TOTAL': costo_total,
                })

            df_resultado = pd.DataFrame(resultados)
    else:
        form = ExcelUploadForm()

    return render(request, 'factores/upload_excel.html', {
        'form': form,
        'tabla': df_resultado.to_html(classes='table table-striped', index=False) if df_resultado is not None else None,
    })

