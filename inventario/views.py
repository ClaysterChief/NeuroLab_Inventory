from django.shortcuts import render
from rest_framework import viewsets
from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios
from .serializers import AnestesicosSerializer, BitacoraSerializer, CajasSerializer, CondicionesSerializer, RatasSerializer, RolesSerializer, TejidosSerializer, UsuariosSerializer

class AnestesicosViewSet(viewsets.ModelViewSet):
    queryset = Anestesicos.objects.all()
    serializer_class = AnestesicosSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        
    def perform_update(self, serializer):
        serializer.save()
        
    def perform_destroy(self, instance):
        instance.delete()
    
class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
class CajasViewSet(viewsets.ModelViewSet):
    queryset = Cajas.objects.all()
    serializer_class = CajasSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
class CondicionesViewSet(viewsets.ModelViewSet):
    queryset = Condiciones.objects.all()
    serializer_class = CondicionesSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
class RatasViewSet(viewsets.ModelViewSet):
    queryset = Ratas.objects.all()
    serializer_class = RatasSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
class TejidosViewSet(viewsets.ModelViewSet):
    queryset = Tejidos.objects.all()
    serializer_class = TejidosSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
        
# Create your views here.