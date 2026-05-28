"""
Serializers del proyecto NeuroLab Inventory.

Incluye los serializers de modelos para la API REST,
y el serializer personalizado para el login con JWT.
"""

import json
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password

from .models import (
    Anestesicos, Bitacora, Cajas, Condiciones,
    Ratas, Roles, Tejidos, Usuarios
)


# ─── Serializers de modelos (API REST) ───────────────────────────────────────

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'


class UsuariosSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.ReadOnlyField()

    # write_only=True → nunca se devuelven en las respuestas JSON
    password = serializers.CharField(
        max_length=128, write_only=True, required=False,
        style={'input_type': 'password'},
        help_text='Obligatorio al crear. Dejar vacío al editar para no cambiarla.'
    )
    password_confirm = serializers.CharField(
        max_length=128, write_only=True, required=False,
        style={'input_type': 'password'},
        help_text='Repetir la contraseña para confirmar.'
    )

    class Meta:
        model = Usuarios
        fields = [
            'idusuario', 'nombreusuario',
            'password', 'password_confirm',       # write-only, no aparecen en GET
            'apellidopaterno', 'apellidomaterno',
            'idrol', 'rol_nombre', 'sexo',
        ]

    def validate(self, attrs):
        password = attrs.get('password', '')
        password_confirm = attrs.pop('password_confirm', '')  # quitar del dict final

        is_create = self.instance is None  # True = POST, False = PUT/PATCH

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
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Solo cambiar contraseña si se envió una nueva
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


class RatasSerializer(serializers.ModelSerializer):
    condicion_nombre = serializers.ReadOnlyField(source='idcondicion.nombrecondicion')

    class Meta:
        model = Ratas
        fields = '__all__'


class CajasSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.ReadOnlyField(source='idusuario.nombreusuario')

    class Meta:
        model = Cajas
        fields = '__all__'


class BitacoraSerializer(serializers.ModelSerializer):
    anestesico_nombre = serializers.ReadOnlyField(source='idanestesico.nombreanestesico')
    tejido_nombre = serializers.ReadOnlyField(source='idtejido.nombretejido')
    responsable_nombre = serializers.ReadOnlyField(source='idusuario.nombreusuario')

    class Meta:
        model = Bitacora
        fields = '__all__'


# ─── Serializer de autenticación (Login con JWT) ──────────────────────────────

class LoginSerializer(serializers.Serializer):
    """
    Autentica contra la tabla 'usuarios' (no contra django.contrib.auth.User).
    Soporta contraseñas en texto plano (legacy) y hasheadas (PBKDF2).
    Al detectar texto plano, lo hashea automáticamente para futuras sesiones.
    """
    username = serializers.CharField(max_length=45)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')

        # 1. Buscar el usuario
        try:
            user = Usuarios.objects.select_related('idrol').get(
                nombreusuario=username
            )
        except Usuarios.DoesNotExist:
            # Mismo mensaje para usuario no existe y contraseña incorrecta
            # (evitar enumeración de usuarios)
            raise serializers.ValidationError(
                {'non_field_errors': ['Credenciales inválidas']}
            )

        # 2. Verificar contraseña
        # NOTA: is_password_usable() devuelve True incluso para texto plano
        # (solo devuelve False si empieza con '!'). Por eso usamos una
        # detección más robusta: verificar si parece un hash de Django.
        password_valid = False
        stored = user.password or ''

        DJANGO_HASH_PREFIXES = (
            'pbkdf2_sha256$', 'pbkdf2_sha1$',
            'argon2', 'bcrypt',
            'sha1$', 'md5$',        # hashes legacy de Django
        )

        if any(stored.startswith(p) for p in DJANGO_HASH_PREFIXES):
            # Contraseña ya hasheada con Django → verificación segura
            password_valid = check_password(password, stored)
        else:
            # Contraseña en texto plano (legacy)
            password_valid = (stored == password)
            if password_valid:
                # Migración automática: hashear para futuras sesiones
                user.password = make_password(password)
                user.save(update_fields=['password'])

        if not password_valid:
            raise serializers.ValidationError(
                {'non_field_errors': ['Credenciales inválidas']}
            )

        # 3. Generar tokens JWT con claims personalizados
        refresh = RefreshToken()
        # Claims en el refresh token
        refresh['user_id'] = user.idusuario
        refresh['username'] = user.nombreusuario
        refresh['role_id'] = user.rol_id
        refresh['role_name'] = user.rol_nombre

        # El access token hereda los claims del refresh token en simplejwt
        access = refresh.access_token
        access['user_id'] = user.idusuario
        access['username'] = user.nombreusuario
        access['role_id'] = user.rol_id
        access['role_name'] = user.rol_nombre

        return {
            'access': str(access),
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
