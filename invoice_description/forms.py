# invoice_description/forms.py
from django import forms

class PDFUploadForm(forms.Form):
    archivo = forms.FileField()
