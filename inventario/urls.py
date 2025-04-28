from django.urls import path
from .views import AnestesicosList, AnestesicosDetail, BitacoraList, BitacoraDetail, CajasList, CajasDetail, CondicionesList, CondicionesDetail, RatasList, RatasDetail, RolesList, RolesDetail, TejidosList, TejidosDetail, UsuariosList, UsuariosDetail

urlpatterns = [
    path('anestesicos/', AnestesicosList.as_view(), name='anestesicos-list'),
    path('anestesicos/<int:pk>/', AnestesicosDetail.as_view(), name='anestesicos-detail'),

    path('bitacora/', BitacoraList.as_view(), name='bitacora-list'),
    path('bitacora/<int:pk>/', BitacoraDetail.as_view(), name='bitacora-detail'),

    path('cajas/', CajasList.as_view(), name='cajas-list'),
    path('cajas/<int:pk>/', CajasDetail.as_view(), name='cajas-detail'),

    path('condiciones/', CondicionesList.as_view(), name='condiciones-list'),
    path('condiciones/<int:pk>/', CondicionesDetail.as_view(), name='condiciones-detail'),

    path('ratas/', RatasList.as_view(), name='ratas-list'),
    path('ratas/<int:pk>/', RatasDetail.as_view(), name='ratas-detail'),

    path('roles/', RolesList.as_view(), name='roles-list'),
    path('roles/<int:pk>/', RolesDetail.as_view(), name='roles-detail'),

    path('tejidos/', TejidosList.as_view(), name='tejidos-list'),
    path('tejidos/<int:pk>/', TejidosDetail.as_view(), name='tejidos-detail'),

    path('usuarios/', UsuariosList.as_view(), name='usuarios-list'),
    path('usuarios/<int:pk>/', UsuariosDetail.as_view(), name='usuarios-detail'),
]
