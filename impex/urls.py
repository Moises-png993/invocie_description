"""
URL configuration for impex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# impex/urls.py
from django.contrib import admin
from django.urls import path, include
from invoice_description.views import procesar_pdf, convert_pdf_to_xlsx
from simpex.views import login_view

urlpatterns = [
    path('', login_view, name='login'),
    path('admin/', admin.site.urls),
    path('pdf/', procesar_pdf, name='procesar_pdf'),
    path('convertir-pdf/', convert_pdf_to_xlsx, name='convert_pdf_to_xlsx'),
    path('app/', include('simpex.urls')),
]
