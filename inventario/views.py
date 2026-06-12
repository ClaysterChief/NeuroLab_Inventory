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
from .reports import (
    generate_bitacora_pdf, generate_inventario_pdf,
    generate_inventario_excel, generate_bitacora_excel,
)
from .filters import BitacoraFilter, CajasFilter, RatasFilter
from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios, PesoSemanal, Ubicaciones
from .permissions import IsAdminRole, ReadOnlyForPracticante
from .serializers import (
    AnestesicosSerializer, BitacoraSerializer, CajasSerializer,
    CondicionesSerializer, RatasSerializer, RolesSerializer,
    TejidosSerializer, UsuariosSerializer, LoginSerializer, PesoSemanalSerializer, UbicacionesSerializer
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
    ).prefetch_related('pesos').all().order_by('sexo', 'idrata')
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

# ─── Reportes Excel ─────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_inventario_excel(request):
    """GET /api/reportes/inventario/excel/"""
    buffer = generate_inventario_excel()
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="inventario_neurolab.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_bitacora_excel(request):
    """GET /api/reportes/bitacora/excel/"""
    buffer = generate_bitacora_excel()
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="bitacora_neurolab.xlsx"'
    return response

# ─── Dashboard con estadísticas ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    from django.utils import timezone
    from django.db.models import Count
    inicio_mes = timezone.now().date().replace(day=1)

    cajas_por_ubicacion = list(
        Cajas.objects
        .values('idubicacion__nombreubicacion')
        .annotate(total=Count('idcaja'))
        .order_by('-total')
    )

    return Response({
        'cajas':              Cajas.objects.count(),
        'ratas_total':        Ratas.objects.count(),
        'ratas_macho':        Ratas.objects.filter(sexo__iexact='Macho').count(),
        'ratas_hembra':       Ratas.objects.filter(sexo__iexact='Hembra').count(),
        'experimentos_total': Bitacora.objects.count(),
        'experimentos_mes':   Bitacora.objects.filter(fechacirujia__gte=inicio_mes).count(),
        'usuarios':           Usuarios.objects.count(),
        'cajas_por_ubicacion': cajas_por_ubicacion,   # ← nuevo
    })

class PesoSemanalViewSet(viewsets.ModelViewSet):
    serializer_class   = PesoSemanalSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]

    def get_queryset(self):
        qs = PesoSemanal.objects.select_related('idrata').all()
        # Filtrar por rata si se pasa el parámetro
        idrata = self.request.query_params.get('idrata')
        if idrata:
            qs = qs.filter(idrata=idrata)
        return qs

class UbicacionesViewSet(viewsets.ModelViewSet):
    queryset           = Ubicaciones.objects.all().order_by('nombreubicacion')
    serializer_class   = UbicacionesSerializer
    permission_classes = [IsAuthenticated, ReadOnlyForPracticante]

from datetime import date as _date

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inventario_sesion_view(request):
    """
    Guarda una sesión semanal completa en una transacción atómica.
    Aplica: actualización de comentarios de cajas, nuevos pesos,
    bajas de ratas y altas de ratas.
    """
    from django.db import transaction
    data = request.data

    try:
        with transaction.atomic():
            res = {
                'pesos_guardados': 0,
                'cajas_actualizadas': 0,
                'ratas_dadas_de_baja': 0,
                'ratas_agregadas': 0,
            }

            # 1. Comentarios de cajas
            for cambio in data.get('cambios_cajas', []):
                n = Cajas.objects.filter(idcaja=cambio['idcaja']).update(
                    comentarios=cambio.get('comentarios', '')
                )
                if n:
                    res['cajas_actualizadas'] += 1

            # 2. Pesos semanales
            fecha_sesion = data.get('fecha') or str(_date.today())
            for p in data.get('nuevos_pesos', []):
                if p.get('peso') is not None:
                    PesoSemanal.objects.create(
                        idrata_id=p['idrata'],
                        fecha=p.get('fecha', fecha_sesion),
                        peso=p['peso'],
                        notas=p.get('notas', '') or '',
                    )
                    res['pesos_guardados'] += 1

            # 3. Bajas (eliminar rata — trigger actualiza CantidadRatas)
            for rid in data.get('bajas_ratas', []):
                Ratas.objects.filter(id=rid).delete()
                res['ratas_dadas_de_baja'] += 1

            # 4. Altas — asignar idrata por sexo
            sex_counter = {}
            for nr in data.get('nuevas_ratas', []):
                sexo = nr.get('sexo', 'Macho')
                if sexo not in sex_counter:
                    ultimo = Ratas.objects.filter(
                        sexo__iexact=sexo
                    ).order_by('-idrata').first()
                    sex_counter[sexo] = (ultimo.idrata if ultimo else 0)
                sex_counter[sexo] += 1
                Ratas.objects.create(
                    idrata=sex_counter[sexo],
                    sexo=sexo,
                    numerocola=nr.get('numerocola'),
                    idcaja_id=nr.get('idcaja') or None,
                    idcondicion_id=nr.get('idcondicion') or None,
                    fechacirugia=nr.get('fechacirugia') or None,
                )
                res['ratas_agregadas'] += 1

        return Response({'ok': True, 'resultados': res})
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=400)
