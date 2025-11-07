from django.urls import path
from . import views

urlpatterns = [
    path('subir-excel/', views.upload_excel, name='upload_excel'),
]
