from django.urls import path
from . import views

urlpatterns = [
    path('subir-excel/', views.upload_excel_view, name='upload_excel'),
    path('descargar-excel/', views.descargar_excel_resultados, name='descargar_excel'),
]
