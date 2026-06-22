from rest_framework import serializers
from .models import LiabilityCategory, Lender, LiabilitySnapshot

class LiabilityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LiabilityCategory
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class LenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lender
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class LiabilitySnapshotSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    lender_name = serializers.CharField(source='lender.name', read_only=True)
    debt_reduced = serializers.SerializerMethodField()

    class Meta:
        model = LiabilitySnapshot
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def get_debt_reduced(self, obj):
        return obj.original_loan_amount - obj.remaining_principal
