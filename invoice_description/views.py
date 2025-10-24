import os
from urllib.parse import quote
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .forms import PDFUploadForm
from .utils import reemplazar_codigos_pdf, reemplazar_texto_pdf,  agregar_simbolo_dollar, reemplazar_origen_pdf
from jwt_utils import require_jwt

# Nuevo: imports para JWT
import jwt
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

# 🔹 Credenciales Aspose
CLIENT_ID = "7dd92a9b-3454-4779-832f-74a51436800c"
CLIENT_SECRET = "1a1b6f4f7c7aecae9441abf0413874f9"
STORAGE_NAME = "Facturas"

# Función para obtener token de Aspose
def get_auth_token():
    url = "https://api.aspose.cloud/connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# -----------------------------------------
# Vista 1: Reemplazar códigos y BULTOS en PDF
# -----------------------------------------
@require_jwt
def procesar_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            bultos = form.cleaned_data.get("bultos")

            # 🔹 Reemplazar artículos desde la DB
            pdf_editado = reemplazar_codigos_pdf(archivo)

            pdf_editado = agregar_simbolo_dollar(pdf_editado)

            pdf_editado = reemplazar_origen_pdf(pdf_editado)
            # 🔹 Reemplazar "BULTOS" si se indica
            if bultos:
                pdf_editado = reemplazar_texto_pdf(pdf_editado, "BULTOS", bultos)

            # 🔹 Concatenar "E" al nombre
            nombre, extension = os.path.splitext(archivo.name)
            nuevo_nombre = f"{nombre}E{extension}"

            response = HttpResponse(pdf_editado, content_type="application/pdf")
            response['Content-Disposition'] = f'attachment; filename="{quote(nuevo_nombre)}"'
            return response
    else:
        form = PDFUploadForm()
    return render(request, "invoice_description/procesar_pdf.html", {"form": form})


# -----------------------------------------
# Vista 2: Convertir PDF a XLSX usando Aspose
# -----------------------------------------
@require_jwt
def convert_pdf_to_xlsx(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            file_name = os.path.splitext(archivo.name)[0]
            new_file_name = f"{file_name}.xlsx"

            temp_upload_path = os.path.join(settings.MEDIA_ROOT, archivo.name)
            temp_output_path = os.path.join(settings.MEDIA_ROOT, new_file_name)

            # Guardar temporalmente el PDF
            with open(temp_upload_path, "wb") as f:
                for chunk in archivo.chunks():
                    f.write(chunk)

            try:
                token = get_auth_token()

                # Subir PDF a Aspose Storage
                upload_url = f"https://api.aspose.cloud/v3.0/pdf/storage/file/{archivo.name}?storageName={STORAGE_NAME}"
                with open(temp_upload_path, "rb") as f:
                    upload_response = requests.put(
                        upload_url,
                        headers={"Authorization": f"Bearer {token}"},
                        files={"file": f}
                    )
                upload_response.raise_for_status()

                # Convertir PDF a XLSX
                convert_url = (
                    f"https://api.aspose.cloud/v3.0/pdf/{archivo.name}/convert/xlsx"
                    f"?outPath={new_file_name}&insertBlankColumnAtFirst=true&minimizeTheNumberOfWorksheets=false&uniformWorksheets=true&storage={STORAGE_NAME}"
                )
                convert_response = requests.put(
                    convert_url,
                    headers={"Authorization": f"Bearer {token}"}
                )
                convert_response.raise_for_status()

                # Descargar XLSX
                download_url = f"https://api.aspose.cloud/v3.0/pdf/storage/file/{new_file_name}?storageName={STORAGE_NAME}"
                download_response = requests.get(download_url, headers={"Authorization": f"Bearer {token}"}, stream=True)
                download_response.raise_for_status()

                with open(temp_output_path, "wb") as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Enviar XLSX al navegador
                with open(temp_output_path, "rb") as f:
                    response = HttpResponse(f.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    response['Content-Disposition'] = f'attachment; filename="{quote(new_file_name)}"'

                # Limpiar archivos temporales
                os.remove(temp_upload_path)
                os.remove(temp_output_path)

                return response

            except Exception as e:
                if os.path.exists(temp_upload_path):
                    os.remove(temp_upload_path)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                return HttpResponse(f"Error durante la conversión: {e}", status=500)
    else:
        form = PDFUploadForm()
    return render(request, "invoice_description/procesar_pdf.html", {"form": form})



