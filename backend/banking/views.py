from rest_framework import viewsets, permissions
from .models import BankAccount, BankAccountSnapshot
from .serializers import BankAccountSerializer, BankAccountSnapshotSerializer

class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BankAccountSnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = BankAccountSnapshot.objects.filter(user=self.request.user)
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            qs = qs.filter(month=month, year=year)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
