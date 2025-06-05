from django.urls import path
from .views import UsuariosViewSet, RatasViewSet, CajasViewSet, BitacoraViewSet, AnestesicosViewSet, TejidosViewSet, CondicionesViewSet, RolesViewSet, login_view
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'usuarios', UsuariosViewSet, basename='usuarios')
router.register(r'ratas', RatasViewSet, basename='ratas')
router.register(r'cajas', CajasViewSet, basename='cajas')
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')
router.register(r'anestesicos', AnestesicosViewSet, basename='anestesicos')
router.register(r'tejidos', TejidosViewSet, basename='tejidos')
router.register(r'condiciones', CondicionesViewSet, basename='condiciones')
router.register(r'roles', RolesViewSet, basename='roles')

urlpatterns = router.urls + [
    path('login/', login_view, name='login'),
]
