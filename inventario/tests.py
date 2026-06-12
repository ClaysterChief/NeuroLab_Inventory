from django.test import TestCase

"""
Tests del sistema NeuroLab Inventory.

Cobertura de los casos de prueba del Capítulo 6 de la tesis:
  CP-01  Login válido
  CP-02  Login inválido
  CP-03  Alta de animal (caja)
  CP-04  Consulta de animales
  CP-05  Actualización de animal
  CP-06  Eliminación (solo Admin)
  CP-07  Registro de bitácora
  CP-08  Endpoint siguiente_id
  CP-09  Control de permisos por rol
"""

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient

from .models import (
    Anestesicos, Bitacora, Cajas, Condiciones,
    Ratas, Roles, Tejidos, Usuarios,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def roles(db):
    admin = Roles.objects.create(idrol=1, nombrerol='Administrador', descripcion='Admin')
    enc   = Roles.objects.create(idrol=2, nombrerol='Encargado',     descripcion='Encargado')
    prac  = Roles.objects.create(idrol=3, nombrerol='Practicante',   descripcion='Practicante')
    return admin, enc, prac


@pytest.fixture
def usuarios(db, roles):
    admin_rol, enc_rol, prac_rol = roles
    admin = Usuarios.objects.create(
        nombreusuario='admin_test',
        password=make_password('admin123'),
        apellidopaterno='Admin', apellidomaterno='Test',
        sexo='Masculino', idrol=admin_rol,
    )
    enc = Usuarios.objects.create(
        nombreusuario='enc_test',
        password=make_password('enc123'),
        apellidopaterno='Enc', apellidomaterno='Test',
        sexo='Masculino', idrol=enc_rol,
    )
    prac = Usuarios.objects.create(
        nombreusuario='prac_test',
        password=make_password('prac123'),
        apellidopaterno='Prac', apellidomaterno='Test',
        sexo='Femenino', idrol=prac_rol,
    )
    return admin, enc, prac


@pytest.fixture
def cond(db):
    return Condiciones.objects.create(nombrecondicion='Intacta', descripcion='Sin lesión')


@pytest.fixture
def anest(db):
    return Anestesicos.objects.create(nombreanestesico='Pentano', descripcion='Anestésico general')


@pytest.fixture
def caja(db):
    return Cajas.objects.create(
        cantidadratas=3, sexo='Macho',
        fechanacimiento='2026-01-01', talla='Grande',
    )


@pytest.fixture
def rata(db, cond, caja):
    return Ratas.objects.create(
        idrata=1, sexo='Macho', numerocola=1,
        idcondicion=cond, idcaja=caja,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def login(username, password):
    c = APIClient()
    res = c.post('/api/login/', {'username': username, 'password': password}, format='json')
    return res.data.get('access'), c


def auth_client(token):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return c


# ── CP-01: Login válido ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_valido(usuarios):
    token, _ = login('admin_test', 'admin123')
    assert token is not None


@pytest.mark.django_db
def test_login_devuelve_datos_usuario(usuarios):
    _, c = login('admin_test', 'admin123')
    res = c.post('/api/login/', {'username': 'admin_test', 'password': 'admin123'}, format='json')
    assert res.status_code == 200
    assert 'access' in res.data
    assert res.data['user']['username'] == 'admin_test'
    assert res.data['user']['role_name'] == 'Administrador'


# ── CP-02: Login inválido ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_usuario_inexistente():
    c = APIClient()
    res = c.post('/api/login/', {'username': 'noexiste', 'password': 'x'}, format='json')
    assert res.status_code == 401


@pytest.mark.django_db
def test_login_contrasena_incorrecta(usuarios):
    c = APIClient()
    res = c.post('/api/login/', {'username': 'admin_test', 'password': 'wrongpass'}, format='json')
    assert res.status_code == 401


# ── CP-03: Alta de caja ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_crear_caja_encargado(usuarios):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.post('/api/cajas/', {
        'cantidadratas': 5, 'sexo': 'Macho',
        'fechanacimiento': '2026-01-01', 'talla': 'Grande',
    }, format='json')
    assert res.status_code == 201
    assert Cajas.objects.filter(cantidadratas=5, sexo='Macho').exists()


@pytest.mark.django_db
def test_practicante_no_puede_crear_caja(usuarios):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.post('/api/cajas/', {
        'cantidadratas': 2, 'sexo': 'Hembra',
        'fechanacimiento': '2026-01-01',
    }, format='json')
    assert res.status_code == 403


# ── CP-04: Consulta de animales ────────────────────────────────────────────────

@pytest.mark.django_db
def test_listar_cajas(usuarios, caja):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.get('/api/cajas/')
    assert res.status_code == 200
    # Respuesta paginada
    assert 'results' in res.data
    assert res.data['count'] >= 1


@pytest.mark.django_db
def test_listar_ratas(usuarios, rata):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.get('/api/ratas/')
    assert res.status_code == 200
    assert res.data['count'] >= 1


@pytest.mark.django_db
def test_filtrar_ratas_por_sexo(usuarios, rata):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.get('/api/ratas/?sexo=Macho')
    assert res.status_code == 200
    assert all(r['sexo'] == 'Macho' for r in res.data['results'])


# ── CP-05: Actualización ──────────────────────────────────────────────────────

@pytest.mark.django_db
def test_actualizar_caja(usuarios, caja):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.patch(f'/api/cajas/{caja.idcaja}/', {'cantidadratas': 10}, format='json')
    assert res.status_code == 200
    caja.refresh_from_db()
    assert caja.cantidadratas == 10


@pytest.mark.django_db
def test_actualizar_rata(usuarios, rata, cond):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.patch(f'/api/ratas/{rata.id}/', {'numerocola': 99}, format='json')
    assert res.status_code == 200
    rata.refresh_from_db()
    assert rata.numerocola == 99


# ── CP-06: Eliminación (solo Admin) ───────────────────────────────────────────

@pytest.mark.django_db
def test_admin_elimina_caja(usuarios, caja):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    res = c.delete(f'/api/cajas/{caja.idcaja}/')
    assert res.status_code == 204
    assert not Cajas.objects.filter(idcaja=caja.idcaja).exists()


@pytest.mark.django_db
def test_encargado_no_puede_eliminar(usuarios, caja):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.delete(f'/api/cajas/{caja.idcaja}/')
    assert res.status_code == 403


# ── CP-07: Registro de bitácora ───────────────────────────────────────────────

@pytest.mark.django_db
def test_crear_bitacora(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.post('/api/bitacora/', {
        'idrata':          rata.id,
        'fechacirujia':    '2026-06-01',
        'idanestesico':    anest.idanestesico,
        'dosistotal':      1.5,
        'pesoexperimento': 320.0,
        'actividad':       'Prueba conductual en laberinto',
    }, format='json')
    assert res.status_code == 201
    assert Bitacora.objects.filter(idrata=rata, dosistotal=1.5).exists()


@pytest.mark.django_db
def test_practicante_no_puede_crear_bitacora(usuarios, rata, anest):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.post('/api/bitacora/', {
        'idrata': rata.id, 'fechacirujia': '2026-06-01',
        'idanestesico': anest.idanestesico,
    }, format='json')
    assert res.status_code == 403


# ── CP-08: Endpoint siguiente_id ──────────────────────────────────────────────

@pytest.mark.django_db
def test_siguiente_id_sin_ratas(usuarios):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.get('/api/ratas/siguiente_id/?sexo=Macho')
    assert res.status_code == 200
    assert res.data['siguiente_id'] == 1


@pytest.mark.django_db
def test_siguiente_id_con_ratas(usuarios, rata):
    """Con M-1 existente, el siguiente para Macho debe ser 2."""
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.get('/api/ratas/siguiente_id/?sexo=Macho')
    assert res.status_code == 200
    assert res.data['siguiente_id'] == 2


@pytest.mark.django_db
def test_siguiente_id_hembra_independiente(usuarios, rata):
    """Hembras tienen secuencia independiente de Machos."""
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.get('/api/ratas/siguiente_id/?sexo=Hembra')
    assert res.status_code == 200
    assert res.data['siguiente_id'] == 1   # Independiente de M-1


@pytest.mark.django_db
def test_siguiente_id_sin_parametro(usuarios):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.get('/api/ratas/siguiente_id/')
    assert res.status_code == 400


# ── CP-09: Permisos por rol ────────────────────────────────────────────────────

@pytest.mark.django_db
def test_sin_token_retorna_401():
    c = APIClient()
    res = c.get('/api/cajas/')
    assert res.status_code == 401


@pytest.mark.django_db
def test_practicante_solo_lectura(usuarios, caja):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    assert c.get('/api/cajas/').status_code        == 200   # lectura: OK
    assert c.post('/api/cajas/', {}).status_code   == 403   # escritura: denegado
    assert c.delete(f'/api/cajas/{caja.idcaja}/').status_code == 403  # delete: denegado


@pytest.mark.django_db
def test_encargado_lectura_escritura_sin_delete(usuarios, caja):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    assert c.get('/api/cajas/').status_code == 200           # lectura: OK
    assert c.delete(f'/api/cajas/{caja.idcaja}/').status_code == 403  # delete: denegado


@pytest.mark.django_db
def test_admin_acceso_total(usuarios, caja):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    assert c.get('/api/cajas/').status_code == 200           # lectura: OK
    assert c.delete(f'/api/cajas/{caja.idcaja}/').status_code == 204  # delete: OK


@pytest.mark.django_db
def test_solo_admin_accede_usuarios(usuarios):
    token_enc,  _ = login('enc_test',  'enc123')
    token_prac, _ = login('prac_test', 'prac123')
    token_adm,  _ = login('admin_test','admin123')
    assert auth_client(token_enc).get('/api/usuarios/').status_code  == 403
    assert auth_client(token_prac).get('/api/usuarios/').status_code == 403
    assert auth_client(token_adm).get('/api/usuarios/').status_code  == 200
