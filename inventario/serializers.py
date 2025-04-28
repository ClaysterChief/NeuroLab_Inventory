from rest_framework import serializers
from .models import Anestesicos, Bitacora, Cajas, Condiciones, Ratas, Roles, Tejidos, Usuarios

class AnestesicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anestesicos
        fields = '__all__'

class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = '__all__'

class CajasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cajas
        fields = '__all__'

class CondicionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condiciones
        fields = '__all__'

class RatasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratas
        fields = '__all__'

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class TejidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tejidos
        fields = '__all__'

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'