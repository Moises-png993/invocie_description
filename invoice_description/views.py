from django.shortcuts import render
from django.http import HttpResponse
from .forms import PDFUploadForm
from .utils import reemplazar_codigos_pdf, reemplazar_texto_pdf

def procesar_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            bultos = form.cleaned_data.get("bultos")

            # 🔹 Paso 1: reemplazar artículos desde la DB
            pdf_editado = reemplazar_codigos_pdf(archivo)

            # 🔹 Paso 2: si hay bultos, reemplazar "BULTOS"
            if bultos:
                pdf_editado = reemplazar_texto_pdf(pdf_editado, "BULTOS", bultos)

            response = HttpResponse(pdf_editado, content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="pdf_editado.pdf"'
            return response
    else:
        form = PDFUploadForm()
    return render(request, "invoice_description/procesar_pdf.html", {"form": form})

