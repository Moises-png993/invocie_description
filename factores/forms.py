from django import forms

class UploadExcelForm(forms.Form):
    # Archivo principal FOB (opcional)
    file_fob = forms.FileField(label="Archivo Excel - FOB", required=False)
    # Archivo con fletes (opcional)
    file_fletes = forms.FileField(label="Archivo Excel - Fletes", required=False)
    # Archivo con cantidades (opcional)
    file_cantidades = forms.FileField(label="Archivo Excel - Cantidades", required=False)


