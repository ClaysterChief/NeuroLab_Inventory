import django_filters
from django.db.models import Q
from .models import Bitacora, Cajas, Ratas


class RatasFilter(django_filters.FilterSet):
    sexo   = django_filters.CharFilter(field_name='sexo',   lookup_expr='iexact')
    idcaja = django_filters.NumberFilter(field_name='idcaja')
    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(numerocola__icontains=value) |
            Q(idcondicion__nombrecondicion__icontains=value)
        )

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
    idanestesico = django_filters.NumberFilter(field_name='idanestesico')
    search       = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(actividad__icontains=value) |
            Q(notas__icontains=value) |
            Q(idusuario__nombreusuario__icontains=value)
        )

    class Meta:
        model = Bitacora
        fields = ['idanestesico']