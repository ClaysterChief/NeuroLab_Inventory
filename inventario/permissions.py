"""
permissions.py — Permisos personalizados por rol.

Roles del sistema (comparados por nombre, case-insensitive):
  - Administrador : lectura + escritura + eliminación en todo
  - Encargado     : lectura + escritura, SIN eliminación
  - Practicante   : solo lectura
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

ROLE_ADMIN    = 'administrador'
ROLE_ENCARGADO = 'encargado'
ROLE_PRACTICANTE = 'practicante'


def get_role(user):
    """Devuelve el nombre del rol en minúsculas o cadena vacía."""
    role = getattr(user, 'rol_nombre', None)
    return (role or '').lower()


class IsAdminRole(BasePermission):
    """Solo el rol Administrador puede operar."""
    message = 'Acción restringida al rol Administrador.'

    def has_permission(self, request, view):
        return get_role(request.user) == ROLE_ADMIN


class IsEncargadoOrAdmin(BasePermission):
    """Administrador y Encargado pueden operar. Practicante: solo lectura."""
    message = 'Necesitas rol Encargado o Administrador para esta acción.'

    def has_permission(self, request, view):
        role = get_role(request.user)
        if request.method in SAFE_METHODS:
            # GET, HEAD, OPTIONS → todos los roles autenticados
            return True
        # Escritura/eliminación → solo Admin y Encargado
        return role in (ROLE_ADMIN, ROLE_ENCARGADO)


class ReadOnlyForPracticante(BasePermission):
    """
    Permiso estándar para la mayoría de los ViewSets:
      - Practicante : GET/HEAD/OPTIONS únicamente
      - Encargado   : GET + POST + PUT/PATCH (sin DELETE)
      - Admin       : todo
    """
    message = 'No tienes permiso para esta acción.'

    def has_permission(self, request, view):
        role = get_role(request.user)

        if request.method in SAFE_METHODS:
            return True   # Lectura: todos los roles

        if request.method == 'DELETE':
            # Eliminar: solo Administrador (RF-003, RF-011)
            return role == ROLE_ADMIN

        # POST, PUT, PATCH: Admin y Encargado (RF-002, RF-010)
        return role in (ROLE_ADMIN, ROLE_ENCARGADO)
