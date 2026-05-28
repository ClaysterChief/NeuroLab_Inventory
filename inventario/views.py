"""
views.py — Vistas de la API NeuroLab Inventory.

Permisos aplicados según el documento (RF-003, RF-010, RF-011):
  - Practicante   : solo lectura (GET)
  - Encargado     : lectura + escritura (POST, PUT, PATCH)
  - Administrador : todo (incluye DELETE y gestión de usuarios)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios
from .serializers import (
    AnestesicosSerializer, BitacoraSerializer, CajasSerializer,
    CondicionesSerializer, RatasSerializer, RolesSerializer,
    TejidosSerializer, UsuariosSerializer, LoginSerializer
)
from .permissions import ReadOnlyForPracticante, IsAdminRole


# ─── Autenticación ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/login/
    Body: { username, password }
    Response: { access, refresh, user }
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(
        {'error': 'Credenciales inválidas'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/me/
    Devuelve los datos del usuario autenticado actualmente.
    Útil para restaurar la sesión al recargar la página.
    """
    user = request.user
    return Response({
        'id': user.idusuario,
        'username': user.nombreusuario,
        'nombre_completo': user.nombre_completo,
        'sexo': user.sexo,
        'role_id': user.rol_id,
        'role_name': user.rol_nombre,
    })


# ─── ViewSets de catálogos ──────────────────────────────────────────────────
# Anestésicos, Tejidos, Condiciones, Roles son catálogos que solo
# el Administrador debería poder modificar.

class AnestesicosViewSet(viewsets.ModelViewSet):
    queryset = Anestesicos.objects.all().order_by('nombreanestesico')
    serializer_class = AnestesicosSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]


class TejidosViewSet(viewsets.ModelViewSet):
    queryset = Tejidos.objects.all().order_by('nombretejido')
    serializer_class = TejidosSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]


class CondicionesViewSet(viewsets.ModelViewSet):
    queryset = Condiciones.objects.all().order_by('nombrecondicion')
    serializer_class = CondicionesSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]


class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all().order_by('idrol')
    serializer_class = RolesSerializer
    # Solo Administrador puede crear/editar/eliminar roles
    permission_classes = [IsAuthenticated, IsAdminRole]


# ─── ViewSets principales ───────────────────────────────────────────────────

class RatasViewSet(viewsets.ModelViewSet):
    """
    Ratas: Practicante = solo lectura.
    Encargado/Admin = lectura + escritura.
    Solo Admin puede eliminar (RF-003).
    """
    queryset = Ratas.objects.select_related('idcondicion').all().order_by('idrata')
    serializer_class = RatasSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]


class CajasViewSet(viewsets.ModelViewSet):
    """
    Cajas (inventario): misma lógica que Ratas.
    """
    queryset = Cajas.objects.select_related('idrata', 'idusuario').all().order_by('idcaja')
    serializer_class = CajasSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]


class BitacoraViewSet(viewsets.ModelViewSet):
    """
    Bitácora experimental:
      - RF-009: registrar → Encargado y Admin
      - RF-010: actualizar → Encargado y Admin
      - RF-011: eliminar   → solo Admin
    """
    queryset = Bitacora.objects.select_related(
        'idrata', 'idusuario', 'idanestesico', 'idtejido'
    ).all().order_by('-idbitacora')
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]


class UsuariosViewSet(viewsets.ModelViewSet):
    """
    Gestión de usuarios: solo Administrador (RF-006).
    """
    queryset = Usuarios.objects.select_related('idrol').all().order_by('idusuario')
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
