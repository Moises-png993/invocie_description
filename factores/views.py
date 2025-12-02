import pandas as pd
from decimal import Decimal
from django.db import transaction
from django.shortcuts import render
from .forms import UploadExcelForm
from .models import Flete, Unidades, Tariff, TariffTable
import openpyxl
from django.http import HttpResponse
from datetime import datetime
from jwt_utils import require_jwt

# --- Utilidades generales ---


def read_excel_file(file, name):
    """Lee un archivo Excel y devuelve un DataFrame validado."""
    if not file.name.lower().endswith('.xlsx'):
        raise ValueError(f"El archivo {name} debe tener extensión .xlsx")
    df = pd.read_excel(file)
    if df.empty:
        raise ValueError(f"El archivo {name} está vacío.")
    return df


def html_table(df):
    """Convierte un DataFrame en tabla HTML Bootstrap."""
    return df.to_html(
        index=False,
        classes="table table-bordered table-striped table-hover align-middle text-center",
        na_rep=""
    )


# --- Procesadores de datos ---

def save_fletes(df):
    """Crea o actualiza registros de Flete a partir del DataFrame."""
    created, updated = 0, 0
    records = df.to_dict(orient='records')

    with transaction.atomic():
        for rec in records:
            pais = rec.get('pais') or rec.get('Pais') or rec.get('PAIS')
            if not pais:
                continue

            def _val(k):
                v = rec.get(k)
                return Decimal(str(v)) if pd.notna(v) and v != '' else None

            defaults = {
                'flete_ipl': _val('flete_ipl') or _val('Flete_IPL'),
                'flete_blue': _val('flete_blue') or _val('Flete_Blue'),
                'flete_directo': _val('flete_directo') or _val('Flete_Directo'),
            }

            obj, is_created = Flete.objects.update_or_create(
                pais=str(pais).strip(),
                defaults=defaults
            )
            if is_created:
                created += 1
            else:
                updated += 1

    return created, updated


def save_unidades(df):
    """Crea o actualiza registros de Unidades."""
    created, updated = 0, 0
    records = df.to_dict(orient='records')

    with transaction.atomic():
        for rec in records:
            grupo = rec.get('grupo_articulo') or rec.get('grupo') or rec.get('Grupo_Articulo')
            if not grupo:
                continue

            def _int_val(k):
                v = rec.get(k)
                if pd.isna(v) or v == '':
                    return None
                try:
                    return int(v)
                except Exception:
                    try:
                        return int(float(v))
                    except Exception:
                        return None

            defaults = {
                'unidades_contenedor': _int_val('unidades_contenedor') or _int_val('Unidades_Contenedor') or 0,
                'unidades_cbm': _int_val('unidades_cbm') or _int_val('Unidades_CBM') or 0,
            }

            obj, is_created = Unidades.objects.update_or_create(
                grupo_articulo=str(grupo).strip(),
                defaults=defaults
            )
            if is_created:
                created += 1
            else:
                updated += 1

    return created, updated

def get_costos_paises():
    """Devuelve un diccionario con los costos por país."""
    costos = {}

    # Selecciona la tabla de tarifas que estás usando
    tabla = TariffTable.objects.get(name="TU_TABLA_DE_TARIFAS")

    # Trae todas las tarifas relacionadas
    tarifas = Tariff.objects.filter(tariff_table=tabla).select_related("country", "cost_type")

    for t in tarifas:
        pais = t.country.code.upper()  # o t.country.name
        tipo = t.cost_type.code  # o .name si prefieres nombres largos
        valor = float(t.value or 0)

        if pais not in costos:
            costos[pais] = {}

        costos[pais][tipo] = valor
    print(costos)
    return costos

def calcular_resultado(df_fob, ruta='IPL'):
    """Realiza el cálculo completo de la tabla resultado."""
    df_fob.columns = [col.strip().upper() for col in df_fob.columns]
    resultados = []

    # ⚡️ Cargar todos los costos una sola vez
    costos_paises = get_costos_paises()

    for _, row in df_fob.iterrows():
        try:
            pais = row.get('PAIS ORIGEN')
            grupo = row.get('GRUPO ARTICULOS')
            
            # Validar que existan los valores requeridos
            if not pais or pd.isna(pais):
                raise ValueError(f"Fila sin 'PAIS ORIGEN' definido. Verifica que todas las filas tengan un país de origen.")
            if not grupo or pd.isna(grupo):
                raise ValueError(f"Fila sin 'GRUPO ARTICULOS' definido en país {pais}. Verifica que todas las filas tengan un grupo de artículos.")
            
            fob_val = float(row.get('FOB') or 0)
            precio_venta = float(row.get('PRECIO DE VENTA') or 0)
            
            # Buscar flete en la base de datos
            try:
                flete = Flete.objects.get(pais__iexact=pais)
            except Flete.DoesNotExist:
                raise ValueError(f"No se encontró información de flete para el país '{pais}'. Verifica que el país esté registrado en la base de datos.")
            
            # Buscar unidades en la base de datos
            try:
                unidades = Unidades.objects.get(grupo_articulo__iexact=grupo)
            except Unidades.DoesNotExist:
                raise ValueError(f"No se encontró información de unidades para el grupo de artículos '{grupo}'. Verifica que el grupo esté registrado en la base de datos.")

            # Seleccionar flete según la ruta
            if ruta == 'BLUE':
                flete_valor = flete.flete_blue
            elif ruta == 'DIRECTO':
                flete_valor = flete.flete_directo
            elif ruta == 'LUNO':
                flete_valor = flete.flete_luno
            else:  
                flete_valor = flete.flete_ipl

            flete_unitario = round(float(flete_valor or 0) / unidades.unidades_contenedor, 5)
            
            if unidades.grupo_articulo[:3] == "TNF" or  unidades.grupo_articulo[:4] == "CATR":
                if ruta == 'BLUE':
                    almacenaje = round((1 / unidades.unidades_cbm) * 0.25 * 270, 5)
                elif ruta == 'IPL':
                    almacenaje = round((1 / unidades.unidades_cbm) * 0.35 * 270, 5)
                else:
                    almacenaje = round((1 / unidades.unidades_cbm) * 270, 5)
            else:
                if ruta == 'BLUE':
                    almacenaje = round((1 / unidades.unidades_cbm) * 0.25 * 60, 5)
                elif ruta == 'IPL':
                    almacenaje = round((1 / unidades.unidades_cbm) * 0.35 * 60, 5)
                else:
                    almacenaje = round((1 / unidades.unidades_cbm) * 60, 5) 

            seguro = round((fob_val + flete_unitario) * 0.002442, 5)

            cfs = round(739 / unidades.unidades_contenedor, 5) if flete.pais.lower() == 'china' else 0
            transporte_local = round(250 / unidades.unidades_contenedor, 5)
            thc = round(450 / unidades.unidades_contenedor, 5)
            cl_asia = round(145 / unidades.unidades_contenedor, 5)
            honorarios = round(90 / unidades.unidades_contenedor, 5)

            if unidades.grupo_articulo[3] == "C":
                recepcion = round(0.35 / 10, 5)
                despacho = 0.25 / 10
            else:
                recepcion = 0.14
                despacho = 0.10

            if unidades.grupo_articulo[:3] == "DSM" or  unidades.grupo_articulo[:3] == "DSP" or  unidades.grupo_articulo[:3] == "DIS":
                royalty = (precio_venta * 0.85) * 0.10
            elif unidades.grupo_articulo[:3] == "HPU":
                royalty = (precio_venta * 0.65) * 0.06
            else:
                royalty = 0
            comision_cat = fob_val * 0.2275 if unidades.grupo_articulo[:4] == "CATC" else 0

            costo_ait = fob_val + flete_unitario + cfs + thc + cl_asia + honorarios + transporte_local + almacenaje + seguro + recepcion + despacho + comision_cat + royalty
            if ruta == 'LUNO':
                comision_ait = round(costo_ait * 0.10, 5)
                print("entre")
            else:
                comision_ait = round(costo_ait * 0.12, 5)
            fob_ait = costo_ait + comision_ait
            
            nodo_proveedor = fob_val + comision_cat + royalty
            nodo_importacion = cfs + flete_unitario + thc + cl_asia  + seguro + transporte_local
            nodo_bfi = honorarios + recepcion + despacho + almacenaje
            nodo_ait_nh = comision_ait

            factor_ait = round(costo_ait / fob_val, 5)
            # =====================
            # Calculo por país genérico
            # =====================
            resultados_pais = {}
            if ruta == 'LUNO':
                cfs = 0
                flete_unitario = 0
                thc = 0
                cl_asia = 0
                honorarios = 0
                transporte_local = 0
                recepcion = 0
                despacho = 0
                almacenaje = 0
                seguro = 0
            if ruta == 'DIRECTO':
                recepcion = 0
                despacho = 0
                transporte_local = 0
                almacenaje = 0
                
                

            for codigo_pais in ['SV', 'GT', 'HN', 'CR', 'PA', 'NI']:
                costo = costos_paises.get(codigo_pais, {})
                
                almacenaje_local = costo.get('almacenaje', 0) / (unidades.unidades_contenedor * 1.54)

                honorarios_aduanales = costo.get('honorarios_aduanales', 0) / (unidades.unidades_contenedor * 1.54)
                flete_local = costo.get('flete_local', 0) / (unidades.unidades_contenedor * 1.54)
                inspection_no_intrusiva = costo.get('inspeccion_intrusiva', 0) / (unidades.unidades_contenedor * 1.54)
                custodio_ca = costo.get('custodio', 0) / (unidades.unidades_contenedor * 1.54)
                flete_terrestre_ca = costo.get('flete_terrestre_ca', 0) / (unidades.unidades_contenedor * 1.54)
                otros_gastos = costo.get('otros_gastos', 0) / (unidades.unidades_contenedor * 1.54)
                seguro_pais = (fob_ait + flete_local) * 0.002442
                if flete.pais.lower() in ('méxico', 'guatemala', 'el salvador', 'alemania', 'nicaragua'):
                    dai_pais = 0
                else:
                    dai_pais = (fob_ait + flete_local + seguro_pais) * 0.15

                nodo_exportacion = honorarios_aduanales + flete_local + seguro_pais + dai_pais + inspection_no_intrusiva + almacenaje_local + custodio_ca + flete_terrestre_ca + otros_gastos
                landed = fob_ait + honorarios_aduanales + flete_local + seguro_pais + dai_pais + inspection_no_intrusiva + almacenaje_local + custodio_ca + flete_terrestre_ca + otros_gastos
                factor = round(landed / fob_val, 5)

                resultados_pais[codigo_pais] = {
                    'HONORARIOS': honorarios_aduanales,
                    'FLETE': flete_local,
                    'SEGURO': seguro_pais,
                    'DAI': dai_pais,
                    'LANDED': landed,
                    'FACTOR': factor,
                    'ALMACENAJE': almacenaje_local,
                    'INSPECCION': inspection_no_intrusiva,
                    'CUSTODIO_CA': custodio_ca,
                    'FLETE_TERRESTRE': flete_terrestre_ca,
                    'OTROS_GASTOS': otros_gastos,
                    'NODO_EXPORTACION': nodo_exportacion,
                }

            resultados.append({
                'PAIS ORIGEN': pais,
                'GRUPO ARTICULOS': grupo,
                'PRECIO DE VENTA': precio_venta,
                'FOB': fob_val,
                'COMISION CAT': comision_cat,
                'ROYALTY': royalty,
                'CFS': cfs,
                'FLETE INTERNACIONAL': flete_unitario,
                'THC': thc,
                'CL ASIA': cl_asia,
                'HONORARIOS BFI': honorarios,
                'TRANSPORTE LOCAL': transporte_local,
                'RECEPCION': recepcion,
                'DESPACHO': despacho,
                'ALMACENAJE BFI': almacenaje,
                'SEGURO IMPORT': seguro,
                'COSTO AIT': costo_ait,
                'COMISION AIT': comision_ait,
                'FOB AIT': fob_ait,
                'NODO PROVEEDOR': nodo_proveedor,
                'NODO IMPORTACION': nodo_importacion,
                'NODO BFI': nodo_bfi,
                'NODO AIT NH': nodo_ait_nh,
                'FACTOR AIT': factor_ait,
                **{f'NODO EXPORTACION {p}': resultados_pais[p]['NODO_EXPORTACION'] for p in resultados_pais},
                # Cargar dinámicamente los resultados por país
                **{f'ALMACENAJE CA {p}': resultados_pais[p]['ALMACENAJE'] for p in resultados_pais},
                **{f'HONORARIOS {p}': resultados_pais[p]['HONORARIOS'] for p in resultados_pais},
                **{f'XRAY {p}': resultados_pais[p]['INSPECCION'] for p in resultados_pais},
                **{f'CUSTODIO {p}': resultados_pais[p]['CUSTODIO_CA'] for p in resultados_pais},
                **{f'FLETE LOCAL PAIS {p}': resultados_pais[p]['FLETE'] for p in resultados_pais},
                **{f'FLETE TERRESTRE {p}': resultados_pais[p]['FLETE_TERRESTRE'] for p in resultados_pais},
                **{f'OTROS GASTOS {p}': resultados_pais[p]['OTROS_GASTOS'] for p in resultados_pais},
                **{f'SEGURO {p}': resultados_pais[p]['SEGURO'] for p in resultados_pais},
                **{f'DAI {p}': resultados_pais[p]['DAI'] for p in resultados_pais},
                **{f'LANDED {p}': resultados_pais[p]['LANDED'] for p in resultados_pais},
                **{f'FACTOR {p}': resultados_pais[p]['FACTOR'] for p in resultados_pais},
                
            })

        except ValueError as e:
            # Re-lanzar errores de validación para que aparezcan en la interfaz
            raise
        except Exception as e:
            print("Error:", e)
            continue

    return pd.DataFrame(resultados) if resultados else None

# --- Vista optimizada ---

@require_jwt
def upload_excel_view(request):
    tablas, errores = {}, []
    stats = {"fletes_created": 0, "fletes_updated": 0, "cant_created": 0, "cant_updated": 0}
    
    # Países disponibles para filtros
    paises = [
        {'codigo': 'SV', 'nombre': 'El Salvador'},
        {'codigo': 'GT', 'nombre': 'Guatemala'},
        {'codigo': 'HN', 'nombre': 'Honduras'},
        {'codigo': 'NI', 'nombre': 'Nicaragua'},
        {'codigo': 'CR', 'nombre': 'Costa Rica'},
        {'codigo': 'PA', 'nombre': 'Panamá'},
    ]

    if request.method == "POST":
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Procesar FOB
                fob_file = form.cleaned_data.get('file_fob')
                ruta = form.cleaned_data.get('ruta', 'IPL')
                
                if fob_file:
                    df_fob = read_excel_file(fob_file, "FOB")
                    tablas["tabla_fob"] = html_table(df_fob)

                # Procesar Fletes
                fletes_file = form.cleaned_data.get('file_fletes')
                if fletes_file:
                    df_fletes = read_excel_file(fletes_file, "Fletes")
                    tablas["tabla_fletes"] = html_table(df_fletes)
                    c, u = save_fletes(df_fletes)
                    stats["fletes_created"], stats["fletes_updated"] = c, u

                # Procesar Cantidades
                cant_file = form.cleaned_data.get('file_cantidades')
                if cant_file:
                    df_cant = read_excel_file(cant_file, "Cantidades")
                    tablas["tabla_cantidades"] = html_table(df_cant)
                    c, u = save_unidades(df_cant)
                    stats["cant_created"], stats["cant_updated"] = c, u

                # Calcular tabla resultado
                if fob_file:
                    df_result = calcular_resultado(df_fob, ruta=ruta)
                    if df_result is not None:
                        tablas["tabla_resultado"] = html_table(df_result)
                        # Guardar resultados en sesión para permitir descarga
                        request.session['resultados'] = df_result.to_dict(orient='records')


            except Exception as e:
                errores.append(str(e))
    else:
        form = UploadExcelForm()

    return render(request, "factores/upload_excel.html", {
        "form": form,
        "paises": paises,
        **tablas,
        **stats,
        "errores": errores,
    })

@require_jwt
def descargar_excel_resultados(request):
    resultados = request.session.get('resultados')

    if not resultados:
        return HttpResponse("No hay resultados disponibles para descargar.", status=400)
    # Obtener país(s) seleccionados (opcional) desde query params: puede ser 'SV' o 'SV,GT'
    pais_param = (request.GET.get('pais') or '').strip()
    selected_paises = [p.strip().upper() for p in pais_param.split(',') if p.strip()]

    # Construir workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"factores_{datetime.now().strftime('%Y%m%d')}"

    # Encabezados disponibles
    headers = list(resultados[0].keys())

    # Columnas base que siempre exportamos (mismo criterio que en template)
    # He agregado columnas calculadas adicionales que se generan en la función
    # `calcular_resultado` para que siempre salgan en el Excel de descarga.
    columnas_base = [
        'PAIS ORIGEN', 'GRUPO ARTICULOS', 'PRECIO DE VENTA', 'FOB', 'COMISION CAT', 'ROYALTY',
        'CFS', 'FLETE INTERNACIONAL', 'THC', 'CL ASIA', 'TRANSPORTE LOCAL', 'RECEPCION', 'DESPACHO',
        'HONORARIOS BFI', 'ALMACENAJE BFI', 'SEGURO IMPORT',
        'COSTO AIT', 'COMISION AIT', 'FOB AIT',
        'NODO PROVEEDOR', 'NODO IMPORTACION', 'NODO BFI', 'NODO AIT NH', 'FACTOR AIT'
    ]

    # Keywords para detectar columnas por país (se combinan con el código de país)
    # Añadimos nodos y exportacion para incluir encabezados como "NODO EXPORTACION SV"
    pais_keywords = [
        'ALMACENAJE', 'HONORARIOS', 'XRAY', 'CUSTODIO', 'FLETE LOCAL', 'FLETE LOCAL PAIS',
        'FLETE TERRESTRE', 'OTROS GASTOS', 'SEGURO', 'DAI', 'LANDED', 'FACTOR',
        'NODO', 'EXPORTACION'
    ]

    # Si no se especifica país, exportar todo
    if not selected_paises:
        filtered_headers = headers
    else:
        filtered_headers = []
        for h in headers:
            h_up = (h or '').upper().strip()
            # normalizar tokens
            tokens = [t for t in __import__('re').sub('[^A-Z0-9]+', ' ', h_up).split() if t]

            # incluir si es columna base
            if any(b in h_up for b in columnas_base):
                filtered_headers.append(h)
                continue

            # detectar keywords y código de país (cualquiera de los seleccionados)
            tiene_keyword = any(k in h_up for k in pais_keywords)
            contiene_pais = any((p in tokens) or ((' ' + p + ' ') in (' ' + h_up + ' ')) for p in selected_paises)
            tiene_sufijo = any(suf in tokens for suf in ('ASI', 'ASIA', 'CA'))

            if tiene_keyword and (contiene_pais or (tiene_sufijo and tokens and tokens[-1] in selected_paises)):
                filtered_headers.append(h)

    # Añadir encabezados al worksheet
    ws.append(filtered_headers)

    # Filas filtradas: mantener solo las claves que están en filtered_headers (mismo orden)
    for fila in resultados:
        row = [fila.get(h) for h in filtered_headers]
        ws.append(row)

    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="factores_{datetime.now().strftime("%Y%m%d")}.xlsx"'

    wb.save(response)
    return response
