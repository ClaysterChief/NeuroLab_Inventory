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
    Ratas, Roles, Tejidos, Usuarios, PesoSemanal,
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


# ── Relleno de huecos de ID (gap-filling) ──────────────────────────────────
# Al eliminar un registro, el siguiente creado debe reutilizar el menor ID
# disponible en vez de seguir incrementando indefinidamente (excepto Ratas,
# que ya maneja su propia numeración por separado).

@pytest.mark.django_db
def test_caja_reutiliza_id_tras_eliminar(usuarios):
    """Si se elimina la Caja #1, la siguiente caja creada debe volver a ser #1."""
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)

    c1 = c.post('/api/cajas/', {'cantidadratas': 1, 'sexo': 'Macho', 'fechanacimiento': '2026-01-01'}, format='json')
    c2 = c.post('/api/cajas/', {'cantidadratas': 1, 'sexo': 'Macho', 'fechanacimiento': '2026-01-01'}, format='json')
    id1, id2 = c1.data['idcaja'], c2.data['idcaja']
    assert id2 == id1 + 1

    # Eliminar la primera caja
    c.delete(f'/api/cajas/{id1}/')

    # La siguiente caja creada debe rellenar el hueco dejado por id1
    c3 = c.post('/api/cajas/', {'cantidadratas': 1, 'sexo': 'Hembra', 'fechanacimiento': '2026-01-01'}, format='json')
    assert c3.status_code == 201
    assert c3.data['idcaja'] == id1


@pytest.mark.django_db
def test_anestesico_reutiliza_id_tras_eliminar(usuarios):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)

    a1 = c.post('/api/anestesicos/', {'nombreanestesico': 'A1', 'descripcion': 'x'}, format='json')
    a2 = c.post('/api/anestesicos/', {'nombreanestesico': 'A2', 'descripcion': 'x'}, format='json')
    id1 = a1.data['idanestesico']

    c.delete(f'/api/anestesicos/{id1}/')

    a3 = c.post('/api/anestesicos/', {'nombreanestesico': 'A3', 'descripcion': 'x'}, format='json')
    assert a3.data['idanestesico'] == id1


@pytest.mark.django_db
def test_ratas_no_rellena_huecos_de_pk(usuarios, cond, caja):
    """
    Las Ratas usan su propio sistema de numeración (idrata por sexo,
    asignado explícitamente por el frontend vía /siguiente_id/) y NO deben
    verse afectadas por la lógica de relleno de huecos de PK que sí aplica
    a Cajas, Anestésicos, Tejidos, Condiciones, Ubicaciones y Usuarios.
    """
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)

    r1 = c.post('/api/ratas/', {
        'idrata': 1, 'sexo': 'Macho', 'numerocola': 5,
        'idcaja': caja.idcaja, 'idcondicion': cond.idcondicion,
    }, format='json')
    r2 = c.post('/api/ratas/', {
        'idrata': 2, 'sexo': 'Macho', 'numerocola': 6,
        'idcaja': caja.idcaja, 'idcondicion': cond.idcondicion,
    }, format='json')
    assert r1.status_code == 201 and r2.status_code == 201

    # Eliminar la primera rata (M-1)
    c.delete(f"/api/ratas/{r1.data['id']}/")

    # Si el endpoint siguiente_id se comportara como el de Cajas (relleno
    # de huecos), devolvería 1. Para Ratas debe seguir devolviendo 3
    # (Max existente + 1), que es el comportamiento ya aceptado por el equipo.
    res = c.get('/api/ratas/siguiente_id/?sexo=Macho')
    assert res.data['siguiente_id'] == 3


# ── Campo nombreproyecto en Bitácora ───────────────────────────────────────

@pytest.mark.django_db
def test_bitacora_guarda_nombreproyecto(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.post('/api/bitacora/', {
        'idrata': rata.id,
        'fechacirujia': '2026-06-01',
        'idanestesico': anest.idanestesico,
        'nombreproyecto': 'Evaluación de memoria espacial',
        'actividad': 'Laberinto en Y',
    }, format='json')
    assert res.status_code == 201
    assert res.data['nombreproyecto'] == 'Evaluación de memoria espacial'


@pytest.mark.django_db
def test_bitacora_nombreproyecto_es_opcional(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.post('/api/bitacora/', {
        'idrata': rata.id,
        'fechacirujia': '2026-06-01',
        'idanestesico': anest.idanestesico,
    }, format='json')
    assert res.status_code == 201


@pytest.mark.django_db
def test_bitacora_busqueda_por_proyecto(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/bitacora/', {
        'idrata': rata.id, 'fechacirujia': '2026-06-01',
        'idanestesico': anest.idanestesico, 'nombreproyecto': 'Estrés crónico',
    }, format='json')
    res = c.get('/api/bitacora/?search=Estrés')
    assert res.status_code == 200
    assert res.data['count'] == 1


# ── Cambio de contraseña propia (cualquier rol) ────────────────────────────

@pytest.mark.django_db
def test_cambiar_password_propia_exitoso(usuarios):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.post('/api/cambiar-password/', {
        'password_actual': 'prac123',
        'password_nueva': 'nuevopass123',
        'password_nueva_confirm': 'nuevopass123',
    }, format='json')
    assert res.status_code == 200

    token2, _ = login('prac_test', 'nuevopass123')
    assert token2 is not None


@pytest.mark.django_db
def test_cambiar_password_actual_incorrecta(usuarios):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.post('/api/cambiar-password/', {
        'password_actual': 'incorrecta',
        'password_nueva': 'nuevopass123',
        'password_nueva_confirm': 'nuevopass123',
    }, format='json')
    assert res.status_code == 400
    assert 'password_actual' in res.data


@pytest.mark.django_db
def test_cambiar_password_confirmacion_no_coincide(usuarios):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.post('/api/cambiar-password/', {
        'password_actual': 'enc123',
        'password_nueva': 'abcdef1',
        'password_nueva_confirm': 'distinto',
    }, format='json')
    assert res.status_code == 400
    assert 'password_nueva_confirm' in res.data


@pytest.mark.django_db
def test_cambiar_password_sin_autenticar():
    c = APIClient()
    res = c.post('/api/cambiar-password/', {
        'password_actual': 'x', 'password_nueva': 'y123456', 'password_nueva_confirm': 'y123456',
    }, format='json')
    assert res.status_code == 401


@pytest.mark.django_db
def test_admin_tambien_puede_cambiar_su_propia_password(usuarios):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    res = c.post('/api/cambiar-password/', {
        'password_actual': 'admin123',
        'password_nueva': 'newadminpass1',
        'password_nueva_confirm': 'newadminpass1',
    }, format='json')
    assert res.status_code == 200


@pytest.mark.django_db
def test_cambiar_password_muy_corta_es_rechazada(usuarios):
    token, _ = login('prac_test', 'prac123')
    c = auth_client(token)
    res = c.post('/api/cambiar-password/', {
        'password_actual': 'prac123',
        'password_nueva': '123',
        'password_nueva_confirm': '123',
    }, format='json')
    assert res.status_code == 400


# ── Búsqueda de Ratas por ID ────────────────────────────────────────────────

@pytest.mark.django_db
def test_busqueda_rata_por_id_con_prefijo_sexo(usuarios, cond, caja):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/ratas/', {'idrata': 5, 'sexo': 'Macho', 'numerocola': 1,
                            'idcaja': caja.idcaja, 'idcondicion': cond.idcondicion}, format='json')
    c.post('/api/ratas/', {'idrata': 5, 'sexo': 'Hembra', 'numerocola': 2,
                            'idcaja': caja.idcaja, 'idcondicion': cond.idcondicion}, format='json')

    res = c.get('/api/ratas/?search=M-5')
    assert res.status_code == 200
    assert res.data['count'] == 1
    assert res.data['results'][0]['sexo'] == 'Macho'


@pytest.mark.django_db
def test_busqueda_rata_por_id_solo_numero(usuarios, cond, caja):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/ratas/', {'idrata': 7, 'sexo': 'Macho', 'numerocola': 1,
                            'idcaja': caja.idcaja, 'idcondicion': cond.idcondicion}, format='json')
    c.post('/api/ratas/', {'idrata': 7, 'sexo': 'Hembra', 'numerocola': 2,
                            'idcaja': caja.idcaja, 'idcondicion': cond.idcondicion}, format='json')

    res = c.get('/api/ratas/?search=7')
    assert res.status_code == 200
    assert res.data['count'] == 2  # coincide con ambas (M-7 y H-7)


@pytest.mark.django_db
def test_busqueda_rata_id_sin_coincidencia_no_revienta(usuarios, cond, caja):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    res = c.get('/api/ratas/?search=texto-no-valido')
    assert res.status_code == 200
    assert res.data['count'] == 0


# ── Filtros de Bitácora: proyecto, responsable, orden por fecha ────────────

@pytest.mark.django_db
def test_filtro_bitacora_por_proyecto(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-01',
                               'idanestesico': anest.idanestesico, 'nombreproyecto': 'Proyecto A'}, format='json')
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-02',
                               'idanestesico': anest.idanestesico, 'nombreproyecto': 'Proyecto B'}, format='json')

    res = c.get('/api/bitacora/?nombreproyecto=Proyecto A')
    assert res.status_code == 200
    assert res.data['count'] == 1
    assert res.data['results'][0]['nombreproyecto'] == 'Proyecto A'


@pytest.mark.django_db
def test_filtro_bitacora_por_responsable(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    enc = Usuarios.objects.get(nombreusuario='enc_test')
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-01',
                               'idanestesico': anest.idanestesico, 'idusuario': enc.idusuario}, format='json')

    res = c.get(f'/api/bitacora/?idusuario={enc.idusuario}')
    assert res.status_code == 200
    assert res.data['count'] == 1


@pytest.mark.django_db
def test_bitacora_proyectos_endpoint_devuelve_lista_unica(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-01',
                               'idanestesico': anest.idanestesico, 'nombreproyecto': 'Proyecto X'}, format='json')
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-02',
                               'idanestesico': anest.idanestesico, 'nombreproyecto': 'Proyecto X'}, format='json')
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-03',
                               'idanestesico': anest.idanestesico, 'nombreproyecto': 'Proyecto Y'}, format='json')

    res = c.get('/api/bitacora/proyectos/')
    assert res.status_code == 200
    assert sorted(res.data) == ['Proyecto X', 'Proyecto Y']


@pytest.mark.django_db
def test_bitacora_ordenar_por_fecha(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-10',
                               'idanestesico': anest.idanestesico}, format='json')
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-01',
                               'idanestesico': anest.idanestesico}, format='json')
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-20',
                               'idanestesico': anest.idanestesico}, format='json')

    res_asc = c.get('/api/bitacora/?ordering=fechacirujia')
    fechas_asc = [r['fechacirujia'] for r in res_asc.data['results']]
    assert fechas_asc == sorted(fechas_asc)

    res_desc = c.get('/api/bitacora/?ordering=-fechacirujia')
    fechas_desc = [r['fechacirujia'] for r in res_desc.data['results']]
    assert fechas_desc == sorted(fechas_desc, reverse=True)


# ── Tarjetas resumen del dashboard (stats_view) ────────────────────────────

@pytest.mark.django_db
def test_stats_incluye_ultima_caja(usuarios, caja):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    res = c.get('/api/stats/')
    assert res.status_code == 200
    assert res.data['ultima_caja'] is not None
    assert res.data['ultima_caja']['idcaja'] == caja.idcaja


@pytest.mark.django_db
def test_stats_ultima_caja_es_la_de_mayor_id(usuarios):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    c.post('/api/cajas/', {'cantidadratas': 1, 'sexo': 'Macho', 'fechanacimiento': '2026-01-01'}, format='json')
    r2 = c.post('/api/cajas/', {'cantidadratas': 2, 'sexo': 'Hembra', 'fechanacimiento': '2026-02-01'}, format='json')
    res = c.get('/api/stats/')
    assert res.data['ultima_caja']['idcaja'] == r2.data['idcaja']


@pytest.mark.django_db
def test_stats_incluye_ultimo_experimento(usuarios, rata, anest):
    token, _ = login('enc_test', 'enc123')
    c = auth_client(token)
    c.post('/api/bitacora/', {'idrata': rata.id, 'fechacirujia': '2026-06-01',
                               'idanestesico': anest.idanestesico, 'nombreproyecto': 'Mi Proyecto'}, format='json')
    res = c.get('/api/stats/')
    assert res.data['ultimo_experimento'] is not None
    assert res.data['ultimo_experimento']['proyecto'] == 'Mi Proyecto'
    assert res.data['ultimo_experimento']['rata'] == 'M-1'


@pytest.mark.django_db
def test_stats_sin_datos_devuelve_none(usuarios):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    res = c.get('/api/stats/')
    assert res.data['ultima_caja'] is None
    assert res.data['ultimo_experimento'] is None
    assert res.data['alerta_peso'] is None


@pytest.mark.django_db
def test_stats_alerta_peso_detecta_bajon(usuarios, rata):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    # Dos pesos: el más reciente es menor → descenso
    PesoSemanal.objects.create(idrata=rata, fecha='2026-06-01', peso=300.0)
    PesoSemanal.objects.create(idrata=rata, fecha='2026-06-08', peso=270.0)
    res = c.get('/api/stats/')
    alerta = res.data['alerta_peso']
    assert alerta is not None
    assert alerta['rata'] == 'M-1'
    assert alerta['variacion_pct'] == -10.0


@pytest.mark.django_db
def test_stats_alerta_peso_none_si_sube(usuarios, rata):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    # El peso sube → no debe haber alerta
    PesoSemanal.objects.create(idrata=rata, fecha='2026-06-01', peso=270.0)
    PesoSemanal.objects.create(idrata=rata, fecha='2026-06-08', peso=300.0)
    res = c.get('/api/stats/')
    assert res.data['alerta_peso'] is None


@pytest.mark.django_db
def test_stats_alerta_peso_elige_el_peor(usuarios, cond, caja):
    token, _ = login('admin_test', 'admin123')
    c = auth_client(token)
    r1 = Ratas.objects.create(idrata=1, sexo='Macho', numerocola=1, idcondicion=cond, idcaja=caja)
    r2 = Ratas.objects.create(idrata=2, sexo='Macho', numerocola=2, idcondicion=cond, idcaja=caja)
    # r1 baja 5%, r2 baja 20% → debe elegir r2
    PesoSemanal.objects.create(idrata=r1, fecha='2026-06-01', peso=300.0)
    PesoSemanal.objects.create(idrata=r1, fecha='2026-06-08', peso=285.0)
    PesoSemanal.objects.create(idrata=r2, fecha='2026-06-01', peso=300.0)
    PesoSemanal.objects.create(idrata=r2, fecha='2026-06-08', peso=240.0)
    res = c.get('/api/stats/')
    assert res.data['alerta_peso']['rata'] == 'M-2'
    assert res.data['alerta_peso']['variacion_pct'] == -20.0
