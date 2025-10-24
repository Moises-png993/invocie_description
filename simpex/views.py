# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Contenedor
# Reemplazado: utilidades JWT locales por import desde jwt_utils
from jwt_utils import create_jwt_for_user, require_jwt
from django.http import JsonResponse, HttpResponse

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			# crear JWT y guardarlo en cookie HttpOnly
			token = create_jwt_for_user(user)
			# Si es una llamada AJAX/API, devolver token en JSON
			if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.headers.get("Accept","").startswith("application/json"):
				resp = JsonResponse({"token": token})
				# opcion: también enviar cookie para navegadores
				resp.set_cookie("jwt", token, httponly=True, samesite='Lax')
				return resp
			response = redirect('home')
			# Ajusta secure=True en producción con HTTPS
			response.set_cookie("jwt", token, httponly=True, samesite='Lax')
			return response
		else:
			messages.error(request, 'Usuario o contraseña incorrectos')
	return render(request, 'simpex/login.html')


@require_jwt
def home(request):
	return render(request, 'simpex/home.html')

@require_jwt
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

def logout_view(request):
	"""Cerrar sesión y borrar cookie JWT."""
	# Si se recibe POST o GET, cerrar sesión y borrar cookie
	logout(request)
	resp = redirect("login")
	resp.delete_cookie("jwt")
	return resp

@require_jwt
def refresh_jwt(request):
	"""Regenerar y devolver un nuevo JWT para el usuario autenticado."""
	user = getattr(request, "user", None)
	if not user or not user.is_authenticated:
		return redirect("login")
	new_token = create_jwt_for_user(user)
	# Si es petición AJAX/API devolver JSON
	if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.headers.get("Accept","").startswith("application/json"):
		resp = JsonResponse({"token": new_token})
		resp.set_cookie("jwt", new_token, httponly=True, samesite='Lax')
		return resp
	# Para navegación normal, actualizar cookie y redirigir a home
	resp = redirect("home")
	resp.set_cookie("jwt", new_token, httponly=True, samesite='Lax')
	return resp
