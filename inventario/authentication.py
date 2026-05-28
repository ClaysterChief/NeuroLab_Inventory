"""
Autenticación JWT personalizada para el modelo Usuarios.

Django REST Framework espera un objeto 'user' con ciertos atributos.
Como nuestro modelo Usuarios no extiende AbstractBaseUser, esta clase
actúa como puente: valida el token JWT y devuelve el objeto Usuarios
correspondiente como usuario autenticado.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


class UsuariosJWTAuthentication(BaseAuthentication):
    """
    Valida el header 'Authorization: Bearer <token>' contra
    la tabla 'usuarios' de la BD, sin depender del sistema
    de auth de Django (django.contrib.auth.User).
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')

        # Si no hay header, no es un error: la vista puede ser pública
        if not auth_header.startswith('Bearer '):
            return None

        token_str = auth_header.split(' ', 1)[1].strip()
        if not token_str:
            return None

        try:
            # Valida firma, expiración y estructura del token
            token = AccessToken(token_str)
        except (TokenError, InvalidToken) as exc:
            raise AuthenticationFailed(f'Token inválido o expirado: {exc}')

        # Obtener el usuario desde la BD usando el claim 'user_id' del token
        user_id = token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('El token no contiene user_id')

        # Importar aquí para evitar circular imports
        from .models import Usuarios
        try:
            user = Usuarios.objects.select_related('idrol').get(idusuario=user_id)
        except Usuarios.DoesNotExist:
            raise AuthenticationFailed('Usuario del token no encontrado')

        return (user, token)

    def authenticate_header(self, request):
        """
        Devuelve el valor del header WWW-Authenticate cuando la
        autenticación falla, para que el cliente sepa qué esquema usar.
        """
        return 'Bearer realm="api"'
