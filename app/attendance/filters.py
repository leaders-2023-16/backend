import django_filters
from attendance.models import Report


class ReportFilterSet(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Report
        fields = [
            "date_from",
            "date_to",
            "date",
            "is_approved",
            "work_place",
            "approved_by",
        ]
