import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 60 * 60  # 1 hora

def create_jwt_for_user(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_jwt_token(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])

def require_jwt(view_func):
    """Decorador para proteger vistas: busca token en Authorization Bearer o cookie 'jwt'."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        token = None
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        if not token:
            token = request.COOKIES.get("jwt")
        if not token:
            messages.error(request, "Por favor, inicie sesión")
            return redirect("login")
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get("user_id")
            user = User.objects.get(pk=user_id)
            request.user = user
        except Exception:
            messages.error(request, "Token inválido o expirado. Inicie sesión de nuevo.")
            resp = redirect("login")
            resp.delete_cookie("jwt")
            return resp
        return view_func(request, *args, **kwargs)
    return _wrapped
