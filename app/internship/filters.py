import django_filters
from internship.models import Event


class EventFilterSet(django_filters.FilterSet):
    datetime_from = django_filters.DateTimeFilter(
        field_name="datetime", lookup_expr="gte"
    )
    datetime_to = django_filters.DateTimeFilter(
        field_name="datetime", lookup_expr="lte"
    )

    class Meta:
        model = Event
        fields = [
            "datetime_from",
            "datetime_to",
        ]
