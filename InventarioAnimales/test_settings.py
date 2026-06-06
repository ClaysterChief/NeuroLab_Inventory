from InventarioAnimales.settings import *

# SQLite en memoria: rápido, sin permisos MySQL, sin BD de prueba externa
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   ':memory:',
    }
}