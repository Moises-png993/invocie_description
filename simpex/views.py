
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Contenedor

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'simpex/login.html')


def home(request):
    return render(request, 'simpex/home.html')

def dashboard(request):
    pais = request.GET.get("pais")
    status = request.GET.get("status")
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    queryset = Contenedor.objects.all()

    if pais and pais != "Todos":
        queryset = queryset.filter(pais__icontains=pais)
    if status and status != "Todos":
        queryset = queryset.filter(status=status)
    if fecha_desde:
        queryset = queryset.filter(eta__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(eta__lte=fecha_hasta)

    context = {"contenedores": queryset}
    return render(request, "simpex/export.html", context)
