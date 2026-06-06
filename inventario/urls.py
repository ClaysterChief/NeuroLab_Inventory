from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnestesicosViewSet, BitacoraViewSet, CajasViewSet,
    CondicionesViewSet, RatasViewSet, RolesViewSet,
    TejidosViewSet, UsuariosViewSet, login_view, me_view,
    reporte_bitacora, reporte_inventario,
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

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('me/', me_view, name='me'),
    path('reportes/inventario/', reporte_inventario, name='reporte_inventario'),
    path('reportes/bitacora/', reporte_bitacora, name='reporte_bitacora'),
]
