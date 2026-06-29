from rest_framework import serializers
from .models import FinancialGoal

class FinancialGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialGoal
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}
