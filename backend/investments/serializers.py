from rest_framework import serializers
from .models import InvestmentCategory, InvestmentPlatform, InvestmentSnapshot

class InvestmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentCategory
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class InvestmentPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPlatform
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class InvestmentSnapshotSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    absolute_profit = serializers.SerializerMethodField()
    profit_percentage = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentSnapshot
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'category': {'required': False}
        }

    def get_absolute_profit(self, obj):
        return round(obj.current_balance - obj.total_invested, 2)

    def get_profit_percentage(self, obj):
        if obj.total_invested > 0:
            return round(((obj.current_balance - obj.total_invested) / obj.total_invested) * 100, 2)
        return 0.00
