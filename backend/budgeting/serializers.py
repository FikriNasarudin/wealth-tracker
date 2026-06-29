from rest_framework import serializers
from .models import TransactionCategory, Transaction, BudgetTarget, Subscription

class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class BudgetTargetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BudgetTarget
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class SubscriptionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}
