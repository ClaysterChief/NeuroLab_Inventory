"""
views.py — Vistas de la API NeuroLab Inventory.

Permisos:
  Practicante   → solo lectura
  Encargado     → lectura + escritura (sin DELETE)
  Administrador → todo
"""
from django.db.models import Max
from .pagination import StandardPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from .reports import generate_bitacora_pdf, generate_inventario_pdf
from .filters import BitacoraFilter, CajasFilter, RatasFilter
from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios
from .permissions import IsAdminRole, ReadOnlyForPracticante
from .serializers import (
    AnestesicosSerializer, BitacoraSerializer, CajasSerializer,
    CondicionesSerializer, RatasSerializer, RolesSerializer,
    TejidosSerializer, UsuariosSerializer, LoginSerializer,
)


# ─── Autenticación ─────────────────────────────────────────────────────────────

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
        'id':             user.idusuario,
        'username':       user.nombreusuario,
        'nombre_completo': user.nombre_completo,
        'sexo':           user.sexo,
        'role_id':        user.rol_id,
        'role_name':      user.rol_nombre,
    })


# ─── Catálogos ─────────────────────────────────────────────────────────────────

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
    permission_classes = [IsAuthenticated, IsAdminRole]


# ─── Cajas ─────────────────────────────────────────────────────────────────────

class CajasViewSet(viewsets.ModelViewSet):
    queryset = Cajas.objects.select_related('idusuario').all().order_by('idcaja')
    serializer_class = CajasSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CajasFilter
    pagination_class = StandardPagination


# ─── Ratas ─────────────────────────────────────────────────────────────────────

class RatasViewSet(viewsets.ModelViewSet):
    queryset = Ratas.objects.select_related(
        'idcondicion', 'idcaja'
    ).all().order_by('sexo', 'idrata')
    serializer_class = RatasSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RatasFilter
    pagination_class = StandardPagination

    @action(detail=False, methods=['get'], url_path='siguiente_id')
    def siguiente_id(self, request):
        """
        GET /api/ratas/siguiente_id/?sexo=Macho
        Devuelve el próximo idrata disponible para el sexo indicado.
        Las secuencias M y H son independientes.
        """
        sexo = request.query_params.get('sexo', '').strip()
        if not sexo:
            return Response(
                {'error': 'El parámetro sexo es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        max_id = Ratas.objects.filter(
            sexo__iexact=sexo
        ).aggregate(Max('idrata'))['idrata__max']
        return Response({'siguiente_id': (max_id or 0) + 1, 'sexo': sexo})


# ─── Bitácora ──────────────────────────────────────────────────────────────────

class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.select_related(
        'idrata', 'idusuario', 'idanestesico', 'idtejido'
    ).all().order_by('-idbitacora')
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BitacoraFilter
    pagination_class = StandardPagination


# ─── Usuarios ──────────────────────────────────────────────────────────────────

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.select_related('idrol').all().order_by('idusuario')
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    pagination_class = StandardPagination


# ─── Reportes PDF ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_inventario(request):
    """GET /api/reportes/inventario/ — Descarga PDF del inventario."""
    buffer = generate_inventario_pdf()
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventario_neurolab.pdf"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_bitacora(request):
    """GET /api/reportes/bitacora/ — Descarga PDF de la bitácora."""
    buffer = generate_bitacora_pdf()
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bitacora_neurolab.pdf"'
    return response    