import re
import django_filters
from django.db.models import Q
from .models import Bitacora, Cajas, Ratas


class RatasFilter(django_filters.FilterSet):
    sexo   = django_filters.CharFilter(field_name='sexo',   lookup_expr='iexact')
    idcaja = django_filters.NumberFilter(field_name='idcaja')
    search = django_filters.CharFilter(method='filter_search')

    # Acepta "3", "M-3", "H12", "m 7" (con o sin guion/espacio, sin
    # distinguir mayúsculas) y filtra por el ID de rata mostrado en la UI.
    _ID_PATTERN = re.compile(r'^([MmHh])[\s\-]?(\d+)$')

    def filter_search(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset

        match = self._ID_PATTERN.match(value)
        if match:
            prefix, numero = match.groups()
            sexo = 'Macho' if prefix.upper() == 'M' else 'Hembra'
            return queryset.filter(sexo=sexo, idrata=int(numero))

        if value.isdigit():
            return queryset.filter(idrata__icontains=value)

        # La búsqueda está dedicada a ID de rata; si no coincide con
        # ningún formato de ID válido, no hay resultados.
        return queryset.none()

    class Meta:
        model = Ratas
        fields = ['sexo', 'idcaja']


class CajasFilter(django_filters.FilterSet):
    sexo   = django_filters.CharFilter(field_name='sexo', lookup_expr='iexact')
    idubicacion = django_filters.NumberFilter(field_name='idubicacion')
    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(comentarios__icontains=value) |
            Q(idusuario__nombreusuario__icontains=value) |
            Q(idusuario__apellidopaterno__icontains=value)
        )

    class Meta:
        model = Cajas
        fields = ['sexo', 'idubicacion']


class BitacoraFilter(django_filters.FilterSet):
    idanestesico   = django_filters.NumberFilter(field_name='idanestesico')
    nombreproyecto = django_filters.CharFilter(field_name='nombreproyecto', lookup_expr='icontains')
    idusuario      = django_filters.NumberFilter(field_name='idusuario')
    search         = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(actividad__icontains=value) |
            Q(notas__icontains=value) |
            Q(nombreproyecto__icontains=value) |
            Q(idusuario__nombreusuario__icontains=value)
        )

    class Meta:
        model = Bitacora
        fields = ['idanestesico', 'nombreproyecto', 'idusuario']