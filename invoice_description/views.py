# invoice_description/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .forms import PDFUploadForm
from .utils import reemplazar_codigos_pdf

def procesar_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            pdf_editado = reemplazar_codigos_pdf(archivo)

            response = HttpResponse(pdf_editado, content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="pdf_editado.pdf"'
            return response
    else:
        form = PDFUploadForm()
    return render(request, "invoice_description/procesar_pdf.html", {"form": form})
