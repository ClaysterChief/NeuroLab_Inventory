from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventario.urls')),
    # /api/login/        → login personalizado (usa tabla 'usuarios')
    # /api/me/           → datos del usuario autenticado
    # /api/token/refresh → renovar access token con el refresh token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
