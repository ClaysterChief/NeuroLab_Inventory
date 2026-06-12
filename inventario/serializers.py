from django.db.models import Max
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password

from .models import (
    Anestesicos, Bitacora, Cajas, Condiciones,
    Ratas, Roles, Tejidos, Usuarios, PesoSemanal, Ubicaciones
)


# ─── Catálogos ────────────────────────────────────────────────────────────────

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'


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


# ─── Cajas ────────────────────────────────────────────────────────────────────

class CajasSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.ReadOnlyField(source='idusuario.nombreusuario')
    ubicacion_nombre   = serializers.ReadOnlyField(source='idubicacion.nombreubicacion')

    class Meta:
        model  = Cajas
        fields = '__all__'

class CajaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cajas
        fields = ['idcaja', 'sexo', 'cantidadratas', 'talla']
        
# ─── Ratas ────────────────────────────────────────────────────────────────────

class RatasSerializer(serializers.ModelSerializer):
    condicion_nombre = serializers.ReadOnlyField(source='idcondicion.nombrecondicion')
    caja_info        = CajaInfoSerializer(source='idcaja', read_only=True)
    idcaja           = serializers.PrimaryKeyRelatedField(
        queryset=Cajas.objects.all(), allow_null=True, required=False,
    )
    # Último peso desde historial — fuente única de verdad
    ultimo_peso      = serializers.SerializerMethodField()
    ultima_fecha_peso = serializers.SerializerMethodField()

    def get_ultimo_peso(self, obj):
        ultimo = obj.pesos.first()   # pesos ordenados por -fecha
        return ultimo.peso if ultimo else None

    def get_ultima_fecha_peso(self, obj):
        ultimo = obj.pesos.first()
        return str(ultimo.fecha) if ultimo else None

    class Meta:
        model  = Ratas
        fields = '__all__'
        extra_kwargs = {'idrata': {'required': False}}

    def validate(self, attrs):
        idrata = attrs.get('idrata')
        sexo   = attrs.get('sexo', '')
        if not idrata:
            from django.db.models import Max
            max_id = Ratas.objects.filter(
                sexo__iexact=sexo
            ).aggregate(Max('idrata'))['idrata__max']
            attrs['idrata'] = (max_id or 0) + 1
            return attrs
        qs = Ratas.objects.filter(idrata=idrata, sexo__iexact=sexo)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            prefix = sexo[0] if sexo else '?'
            raise serializers.ValidationError({
                'idrata': f'Ya existe una rata {prefix}-{idrata}. Elige otro ID.'
            })
        return attrs

# ─── Bitácora ─────────────────────────────────────────────────────────────────

class BitacoraSerializer(serializers.ModelSerializer):
    anestesico_nombre = serializers.ReadOnlyField(source='idanestesico.nombreanestesico')
    tejido_nombre = serializers.ReadOnlyField(source='idtejido.nombretejido')
    responsable_nombre = serializers.ReadOnlyField(source='idusuario.nombreusuario')
    # Campos de la rata para mostrar en la tabla (ej. "M-3")
    rata_sexo = serializers.ReadOnlyField(source='idrata.sexo')
    rata_idlab = serializers.ReadOnlyField(source='idrata.idrata')

    class Meta:
        model = Bitacora
        fields = '__all__'


# ─── Login ────────────────────────────────────────────────────────────────────

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

        password_valid = False
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
        

class PesoSemanalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PesoSemanal
        fields = '__all__'

# ─── Ubicaciones ──────────────────────────────────────────────────────────────

class UbicacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ubicaciones
        fields = '__all__'