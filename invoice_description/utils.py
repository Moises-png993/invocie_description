# invoice_description/utils.py
import fitz  # PyMuPDF
from .models import Articulo
import io

def reemplazar_codigos_pdf(file_obj):
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")

    for pagina in doc:
        for articulo in Articulo.objects.all():
            instancias = pagina.search_for(articulo.codigo)
            for rect in instancias:
                rect_ajustado = fitz.Rect(
                    rect.x0 + 200,
                    rect.y0 ,
                    rect.x1 + 326,
                    rect.y1 
                )
                # Cubrir texto original
                pagina.draw_rect(rect_ajustado, fill=(1, 1, 1), color=(1, 1, 1))

                # Insertar descripción
                punto = fitz.Point(rect.x0+199, rect.y0 + 4.5)
                pagina.insert_text(
                    punto,
                    articulo.descripcion,
                    fontsize=7.2,
                    color=(0, 0, 0)
                )

    salida = io.BytesIO()
    doc.save(salida)
    doc.close()
    salida.seek(0)
    return salida

def reemplazar_origen_pdf(file_obj):
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")

    for pagina in doc:
        for origen in Origen.objects.all():
            instancias = pagina.search_for(origen.codigo)
            for rect in instancias:
                rect_ajustado = fitz.Rect(
                    rect.x0 + 360,
                    rect.y0 ,
                    rect.x1 + 371,
                    rect.y1 
                )
                # Cubrir texto original
                pagina.draw_rect(rect_ajustado, fill=(1, 1, 1), color=(1, 1, 1))

                # Insertar descripción
                punto = fitz.Point(rect.x0+362, rect.y0 + 4.5)
                pagina.insert_text(
                    punto,
                    origen.origen,
                    fontsize=7.2,
                    color=(0, 0, 0)
                )

    salida = io.BytesIO()
    doc.save(salida)
    doc.close()
    salida.seek(0)
    return salida


def reemplazar_texto_pdf(file_obj, buscar, reemplazar):
    """
    Reemplaza un texto específico en el PDF (ejemplo: 'BULTOS' -> '100').
    """
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")

    for pagina in doc:
        instancias = pagina.search_for(buscar)
        for rect in instancias:
            rect_ajustado = fitz.Rect(
                rect.x0 + 37,
                rect.y0,
                rect.x1 + 37,
                rect.y1
            )
            pagina.draw_rect(rect_ajustado, fill=(1, 1, 1), color=(1, 1, 1))

            punto = fitz.Point(rect.x0 + 39, rect.y0 + 6)
            pagina.insert_text(
                punto,
                reemplazar,
                fontsize=8,
                color=(0, 0, 0)
            )

    salida = io.BytesIO()
    doc.save(salida)
    doc.close()
    salida.seek(0)
    return salida

def agregar_simbolo_dollar(file_obj):
    reemplazos = [
        ("FLETE", "$", 130, 6),
        ("SEGURO", "$", 135, 6)
    ]

    doc = fitz.open(stream=file_obj.read(), filetype="pdf")

    for pagina in doc:
        for buscar, reemplazar, x_offset, y_offset in reemplazos:
            instancias = pagina.search_for(buscar)
            for rect in instancias:
                # Ajusta el rectángulo y punto de inserción

                punto = fitz.Point(rect.x0 + x_offset + 2, rect.y0 + y_offset)

                pagina.insert_text(punto, reemplazar, fontsize=8, color=(0, 0, 0))
    salida = io.BytesIO()
    doc.save(salida)
    doc.close()
    salida.seek(0)
    return salida

