"""
utils.py — Utilidades compartidas para el sistema NeuroLab Inventory.

assign_next_available_id() / create_with_next_available_id():
    MariaDB (como la mayoría de motores SQL) nunca reutiliza un ID
    AUTO_INCREMENT después de eliminarlo, así que si se borra la Caja #1
    la siguiente caja creada será la #8 (o el contador que sea), nunca
    vuelve a ser la #1. Para el resto de los catálogos del sistema
    (Cajas, Anestésicos, Tejidos, Condiciones, Ubicaciones, Usuarios,
    Bitácora) el equipo prefiere que el sistema "rellene huecos": que el
    siguiente registro creado tome el menor ID disponible.

    Las Ratas quedan FUERA de esta utilidad a propósito: su numeración
    visible (idrata, ej. "M-3") ya es independiente de la PK interna y
    usa su propia lógica (RatasSerializer.validate), que el equipo ya
    da por buena.
"""
from django.db import IntegrityError, transaction


def get_next_available_id(model, pk_field):
    """
    Devuelve el menor entero positivo (>=1) que no esté usado actualmente
    como valor de `pk_field` en `model`.

    Ejemplos:
        IDs existentes [1, 2, 4]  -> devuelve 3 (rellena el hueco)
        IDs existentes [1, 2, 3]  -> devuelve 4 (no hay huecos, sigue la secuencia)
        Sin registros             -> devuelve 1
    """
    used_ids = model.objects.order_by(pk_field).values_list(pk_field, flat=True)
    expected = 1
    for uid in used_ids:
        if uid is None:
            continue
        if uid != expected:
            return expected
        expected += 1
    return expected


def create_with_next_available_id(model, pk_field, validated_data, build_instance=None, max_attempts=5):
    """
    Crea un registro asignando el menor ID disponible (relleno de huecos)
    en lugar de depender del AUTO_INCREMENT de MariaDB.

    Reintenta automáticamente si dos solicitudes simultáneas llegan a
    calcular el mismo ID disponible y chocan al insertar (IntegrityError),
    evitando errores 500 esporádicos bajo uso concurrente.

    `build_instance(data)` permite lógica de creación personalizada (por
    ejemplo, Usuarios necesita hashear la contraseña) en vez del
    `Model.objects.create()` estándar.
    """
    last_error = None
    for _ in range(max_attempts):
        validated_data[pk_field] = get_next_available_id(model, pk_field)
        try:
            with transaction.atomic():
                if build_instance:
                    return build_instance(validated_data)
                return model.objects.create(**validated_data)
        except IntegrityError as exc:
            last_error = exc
            continue
    raise last_error or IntegrityError(
        f'No se pudo asignar un ID disponible para {model.__name__} tras varios intentos.'
    )
