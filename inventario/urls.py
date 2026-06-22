from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventario.views import inventario_sesion_view
from .views import (
    AnestesicosViewSet, BitacoraViewSet, CajasViewSet,
    CondicionesViewSet, RatasViewSet, RolesViewSet,
    TejidosViewSet, UsuariosViewSet, login_view, me_view,
    reporte_bitacora, reporte_inventario, stats_view,
    reporte_inventario_excel, reporte_bitacora_excel, PesoSemanalViewSet, UbicacionesViewSet,
    cambiar_password_view,
)

router = DefaultRouter()
router.register(r'usuarios',    UsuariosViewSet,    basename='usuarios')
router.register(r'ratas',       RatasViewSet,       basename='ratas')
router.register(r'cajas',       CajasViewSet,       basename='cajas')
router.register(r'bitacora',    BitacoraViewSet,    basename='bitacora')
router.register(r'anestesicos', AnestesicosViewSet, basename='anestesicos')
router.register(r'tejidos',     TejidosViewSet,     basename='tejidos')
router.register(r'condiciones', CondicionesViewSet, basename='condiciones')
router.register(r'roles',       RolesViewSet,       basename='roles')
router.register(r'pesos', PesoSemanalViewSet, basename='pesos')
router.register(r'ubicaciones', UbicacionesViewSet, basename='ubicaciones')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('me/', me_view, name='me'),
    path('cambiar-password/', cambiar_password_view, name='cambiar_password'),
    path('reportes/inventario/', reporte_inventario, name='reporte_inventario'),
    path('reportes/bitacora/', reporte_bitacora, name='reporte_bitacora'),
    path('stats/', stats_view, name='stats'),
    path('reportes/inventario/excel/', reporte_inventario_excel, name='reporte_inventario_excel'),
    path('reportes/bitacora/excel/', reporte_bitacora_excel, name='reporte_bitacora_excel'),
    path('inventario/sesion/', inventario_sesion_view, name='inventario_sesion'),
]
