"""
conftest.py — Configuración global de pytest.

Los modelos de inventario tienen managed=False (Django no gestiona su
esquema) porque la BD ya existe. Para los tests necesitamos que Django
cree las tablas en SQLite, por eso activamos managed=True antes de
que pytest-django inicialice la BD de pruebas.
"""
from inventario.models import (
    Anestesicos, Bitacora, Cajas, Condiciones,
    Ratas, Roles, Tejidos, Usuarios, PesoSemanal, Ubicaciones
)

for _m in (Roles, Anestesicos, Condiciones, Tejidos, Ubicaciones, Usuarios, Cajas, Ratas, PesoSemanal, Bitacora):
    _m._meta.managed = True