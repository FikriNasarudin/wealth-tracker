from rest_framework import serializers
from .models import BankAccount, BankAccountSnapshot

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class BankAccountSnapshotSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = BankAccountSnapshot
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}
