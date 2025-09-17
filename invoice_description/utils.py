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
                    rect.x1 + 300,
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
