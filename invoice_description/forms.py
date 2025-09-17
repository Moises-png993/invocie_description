from django import forms

class PDFUploadForm(forms.Form):
    archivo = forms.FileField(label="Seleccionar PDF")
    bultos = forms.CharField(label="Cantidad de bultos", required=False)
