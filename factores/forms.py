from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Subir archivo Excel (.xlsx)')
