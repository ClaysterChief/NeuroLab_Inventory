from django.shortcuts import render
from rest_framework import generics
from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios
from .serializers import AnestesicosSerializer, BitacoraSerializer, CajasSerializer, CondicionesSerializer, RatasSerializer, RolesSerializer, TejidosSerializer, UsuariosSerializer

class AnestesicosList(generics.ListCreateAPIView):
    queryset = Anestesicos.objects.all()
    serializer_class = AnestesicosSerializer

class AnestesicosDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Anestesicos.objects.all()
    serializer_class = AnestesicosSerializer

    def perform_destroy(self, instance):
        instance.delete()
    
class BitacoraList(generics.ListCreateAPIView):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer

class BitacoraDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer

    def perform_destroy(self, instance):
        instance.delete()

class CajasList(generics.ListCreateAPIView):
    queryset = Cajas.objects.all()
    serializer_class = CajasSerializer

class CajasDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cajas.objects.all()
    serializer_class = CajasSerializer

    def perform_destroy(self, instance):
        instance.delete()

class CondicionesList(generics.ListCreateAPIView):
    queryset = Condiciones.objects.all()
    serializer_class = CondicionesSerializer

class CondicionesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Condiciones.objects.all()
    serializer_class = CondicionesSerializer

    def perform_destroy(self, instance):
        instance.delete()

class RatasList(generics.ListCreateAPIView):
    queryset = Ratas.objects.all()
    serializer_class = RatasSerializer

class RatasDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ratas.objects.all()
    serializer_class = RatasSerializer

    def perform_destroy(self, instance):
        instance.delete()
        
class RolesList(generics.ListCreateAPIView):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer
    
class RolesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

    def perform_destroy(self, instance):
        instance.delete()
        
class TejidosList(generics.ListCreateAPIView):
    queryset = Tejidos.objects.all()
    serializer_class = TejidosSerializer
    
class TejidosDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tejidos.objects.all()
    serializer_class = TejidosSerializer

    def perform_destroy(self, instance):
        instance.delete()
        
class UsuariosList(generics.ListCreateAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer

class UsuariosDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer

    def perform_destroy(self, instance):
        instance.delete()

# Create your views here.    