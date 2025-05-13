from django_filters import rest_framework as filters
from .models import WithdrawalRecord, CommissionRecord

class WithdrawalRecordFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = WithdrawalRecord
        fields = ['status', 'start_date', 'end_date']

class CommissionRecordFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = CommissionRecord
        fields = ['status', 'start_date', 'end_date'] 