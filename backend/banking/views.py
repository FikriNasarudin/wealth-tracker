from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import BankAccount, BankAccountSnapshot
from .serializers import BankAccountSerializer, BankAccountSnapshotSerializer

class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = BankAccount.objects.filter(user=self.request.user)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() in ['true', '1']
            qs = qs.filter(is_active=is_active)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not (month and year):
            return Response({'error': 'month and year are required'}, status=400)
            
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({'error': 'Invalid month or year'}, status=400)
            
        accounts = self.get_queryset().filter(is_active=True)
        total_balance = 0
        
        for account in accounts:
            latest_snap = BankAccountSnapshot.objects.filter(
                user=request.user,
                account=account
            ).filter(
                models.Q(year__lt=year) | models.Q(year=year, month__lte=month)
            ).order_by('-year', '-month').first()
            
            if latest_snap:
                total_balance += latest_snap.balance
                
        return Response({'total_balance': float(total_balance)})

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
