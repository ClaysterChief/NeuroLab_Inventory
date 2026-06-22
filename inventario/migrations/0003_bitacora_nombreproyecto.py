# Migración: agrega NombreProyecto a la tabla bitacora.
#
# IMPORTANTE: el modelo Bitacora tiene managed=False (la tabla ya existe
# en MariaDB y Django no gestiona su esquema), así que `python manage.py
# migrate` NO va a crear esta columna en la base de datos real — Django
# ignora operaciones de esquema para modelos no gestionados.
#
# Para pruebas (pytest con --no-migrations) esto no afecta nada, porque
# pytest-django crea las tablas directamente a partir de models.py.
#
# Para la base de datos real (XAMPP/phpMyAdmin) hay que ejecutar manualmente:
#
#     ALTER TABLE bitacora ADD COLUMN NombreProyecto VARCHAR(150) NULL;
#
# Este archivo queda solo como registro histórico del cambio.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_alter_usuarios_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitacora',
            name='nombreproyecto',
            field=models.CharField(blank=True, db_column='NombreProyecto', max_length=150, null=True),
        ),
    ]
