"""
Serializers del proyecto NeuroLab Inventory.
"""
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password

from .models import (
    Anestesicos, Bitacora, Cajas, Condiciones,
    Ratas, Roles, Tejidos, Usuarios
)


# ─── Catálogos ────────────────────────────────────────────────────────────────

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'


class AnestesicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anestesicos
        fields = '__all__'


class CondicionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condiciones
        fields = '__all__'


class TejidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tejidos
        fields = '__all__'


# ─── Usuarios ─────────────────────────────────────────────────────────────────

class UsuariosSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.ReadOnlyField()

    password = serializers.CharField(
        max_length=128, write_only=True, required=False,
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        max_length=128, write_only=True, required=False,
        style={'input_type': 'password'},
    )

    class Meta:
        model = Usuarios
        fields = [
            'idusuario', 'nombreusuario',
            'password', 'password_confirm',
            'apellidopaterno', 'apellidomaterno',
            'idrol', 'rol_nombre', 'sexo',
        ]

    def validate(self, attrs):
        password = attrs.get('password', '')
        password_confirm = attrs.pop('password_confirm', '')
        is_create = self.instance is None

        if is_create and not password:
            raise serializers.ValidationError(
                {'password': 'La contraseña es obligatoria al crear un usuario.'}
            )
        if password:
            if len(password) < 6:
                raise serializers.ValidationError(
                    {'password': 'La contraseña debe tener al menos 6 caracteres.'}
                )
            if password != password_confirm:
                raise serializers.ValidationError(
                    {'password_confirm': 'Las contraseñas no coinciden.'}
                )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuarios(**validated_data)
        user.password = make_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(password)
        instance.save()
        return instance


# ─── Inventario ───────────────────────────────────────────────────────────────

class CajasSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.ReadOnlyField(source='idusuario.nombreusuario')

    class Meta:
        model = Cajas
        fields = '__all__'


class RatasSerializer(serializers.ModelSerializer):
    condicion_nombre = serializers.ReadOnlyField(source='idcondicion.nombrecondicion')
    caja_info = serializers.SerializerMethodField()

    class Meta:
        model = Ratas
        fields = [
            'id',           # PK interna (usada en URLs: PUT /api/ratas/{id}/)
            'idrata',       # Número de laboratorio por sexo (M-1, H-1…)
            'sexo', 'numerocola', 'idcaja',
            'idcondicion', 'condicion_nombre',
            'pesosemanal', 'fechacirugia',
            'caja_info',
        ]
        read_only_fields = ['id']

    def get_caja_info(self, obj):
        if obj.idcaja:
            return {'idcaja': obj.idcaja.idcaja, 'sexo': obj.idcaja.sexo}
        return None

    def validate(self, attrs):
        """
        Unicidad de número de laboratorio por sexo:
        no puede haber dos machos con el mismo idrata,
        ni dos hembras con el mismo idrata.
        """
        idrata = attrs.get('idrata')
        sexo = attrs.get('sexo')

        if idrata and sexo:
            qs = Ratas.objects.filter(idrata=idrata, sexo=sexo)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'idrata': (
                        f'Ya existe una rata {sexo} con el ID {idrata}. '
                        f'El número de laboratorio debe ser único por sexo.'
                    )
                })
        
        # Validar que si se intenta generar idrata automático, no colisione
        if not idrata and sexo:
            siguiente = self._siguiente_id(sexo)
            qs = Ratas.objects.filter(idrata=siguiente, sexo=sexo)
            if qs.exists():
                raise serializers.ValidationError({
                    'idrata': (
                        f'Error al generar ID automático para {sexo}: '
                        f'el ID {siguiente} ya existe. Por favor, especifica un ID manualmente.'
                    )
                })
        return attrs

    def create(self, validated_data):
        """
        Si no se envía idrata, asignar el siguiente disponible para ese sexo.
        """
        from django.db import IntegrityError
        
        sexo = validated_data.get('sexo', 'Macho')
        if not validated_data.get('idrata'):
            validated_data['idrata'] = self._siguiente_id(sexo)
        
        try:
            rata = Ratas(**validated_data)
            rata.save()
            return rata
        except IntegrityError as e:
            if 'unique' in str(e).lower() or 'idrata' in str(e).lower():
                raise serializers.ValidationError({
                    'idrata': (
                        f'Ya existe una rata {sexo} con el ID {validated_data.get("idrata")}. '
                        f'El número de laboratorio debe ser único por sexo.'
                    )
                })
            raise

    @staticmethod
    def _siguiente_id(sexo):
        """Siguiente número de laboratorio disponible para el sexo dado."""
        ultimo = Ratas.objects.filter(sexo=sexo).order_by('-idrata').first()
        return (ultimo.idrata + 1) if ultimo else 1


class BitacoraSerializer(serializers.ModelSerializer):
    anestesico_nombre = serializers.ReadOnlyField(source='idanestesico.nombreanestesico')
    tejido_nombre = serializers.ReadOnlyField(source='idtejido.nombretejido')
    responsable_nombre = serializers.ReadOnlyField(source='idusuario.nombreusuario')
    rata_sexo = serializers.ReadOnlyField(source='idrata.sexo')

    class Meta:
        model = Bitacora
        fields = '__all__'


# ─── Autenticación ────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=45)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')

        try:
            user = Usuarios.objects.select_related('idrol').get(nombreusuario=username)
        except Usuarios.DoesNotExist:
            raise serializers.ValidationError(
                {'non_field_errors': ['Credenciales inválidas']}
            )

        stored = user.password or ''
        DJANGO_HASH_PREFIXES = (
            'pbkdf2_sha256$', 'pbkdf2_sha1$', 'argon2', 'bcrypt', 'sha1$', 'md5$',
        )

        if any(stored.startswith(p) for p in DJANGO_HASH_PREFIXES):
            password_valid = check_password(password, stored)
        else:
            password_valid = (stored == password)
            if password_valid:
                user.password = make_password(password)
                user.save(update_fields=['password'])

        if not password_valid:
            raise serializers.ValidationError(
                {'non_field_errors': ['Credenciales inválidas']}
            )

        refresh = RefreshToken()
        for token in (refresh, refresh.access_token):
            token['user_id']   = user.idusuario
            token['username']  = user.nombreusuario
            token['role_id']   = user.rol_id
            token['role_name'] = user.rol_nombre

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.idusuario,
                'username': user.nombreusuario,
                'nombre_completo': user.nombre_completo,
                'sexo': user.sexo,
                'role_id': user.rol_id,
                'role_name': user.rol_nombre,
            },
        }