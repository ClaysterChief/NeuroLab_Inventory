"""
views.py — Vistas de la API NeuroLab Inventory.

Permisos:
  Practicante   → solo lectura
  Encargado     → lectura + escritura (sin DELETE)
  Administrador → todo
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios
from .serializers import (
    AnestesicosSerializer, BitacoraSerializer, CajasSerializer,
    CondicionesSerializer, RatasSerializer, RolesSerializer,
    TejidosSerializer, UsuariosSerializer, LoginSerializer
)
from .permissions import ReadOnlyForPracticante, IsAdminRole


# ─── Autenticación ──────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    return Response({
        'id': user.idusuario,
        'username': user.nombreusuario,
        'nombre_completo': user.nombre_completo,
        'sexo': user.sexo,
        'role_id': user.rol_id,
        'role_name': user.rol_nombre,
    })


# ─── Catálogos ──────────────────────────────────────────────────────────────

class AnestesicosViewSet(viewsets.ModelViewSet):
    queryset = Anestesicos.objects.all().order_by('nombreanestesico')
    serializer_class = AnestesicosSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    search_fields = ['nombreanestesico', 'descripcion']


class TejidosViewSet(viewsets.ModelViewSet):
    queryset = Tejidos.objects.all().order_by('nombretejido')
    serializer_class = TejidosSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    search_fields = ['nombretejido', 'descripcion']


class CondicionesViewSet(viewsets.ModelViewSet):
    queryset = Condiciones.objects.all().order_by('nombrecondicion')
    serializer_class = CondicionesSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    search_fields = ['nombrecondicion', 'descripcion']


class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all().order_by('idrol')
    serializer_class = RolesSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]


# ─── Inventario ─────────────────────────────────────────────────────────────

class CajasViewSet(viewsets.ModelViewSet):
    queryset = Cajas.objects.select_related('idusuario').all().order_by('idcaja')
    serializer_class = CajasSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sexo', 'idusuario']
    search_fields = ['comentarios', 'sexo']
    ordering_fields = ['idcaja', 'fechanacimiento', 'cantidadratas']


class RatasViewSet(viewsets.ModelViewSet):
    """
    GET /api/ratas/?sexo=Macho          → todas las ratas macho
    GET /api/ratas/?idcaja=3            → ratas de una caja específica
    GET /api/ratas/siguiente_id/?sexo=Macho → próximo ID disponible para ese sexo
    """
    queryset = Ratas.objects.select_related(
        'idcondicion', 'idcaja'
    ).all().order_by('sexo', 'idrata')
    serializer_class = RatasSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sexo', 'idcaja', 'idcondicion']
    search_fields = ['numerocola']
    ordering_fields = ['idrata', 'sexo', 'fechacirugia', 'pesosemanal']

    @action(detail=False, methods=['get'], url_path='siguiente_id')
    def siguiente_id(self, request):
        """
        GET /api/ratas/siguiente_id/?sexo=Macho
        Devuelve el próximo ID disponible para el sexo solicitado.
        """
        sexo = request.query_params.get('sexo', 'Macho')
        if sexo not in ('Macho', 'Hembra'):
            return Response(
                {'error': 'sexo debe ser Macho o Hembra'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ultimo = Ratas.objects.filter(sexo=sexo).order_by('-idrata').first()
        siguiente = (ultimo.idrata + 1) if ultimo else 1
        return Response({'sexo': sexo, 'siguiente_id': siguiente})


class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.select_related(
        'idrata', 'idusuario', 'idanestesico', 'idtejido'
    ).all().order_by('-idbitacora')
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['idrata', 'idusuario', 'idanestesico', 'idtejido']
    search_fields = ['actividad', 'notas', 'idusuario__nombreusuario']
    ordering_fields = ['idbitacora', 'fechacirujia', 'pesoexperimento']


# ─── Usuarios ───────────────────────────────────────────────────────────────

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.select_related('idrol').all().order_by('idusuario')
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    search_fields = ['nombreusuario', 'apellidopaterno', 'apellidomaterno']
