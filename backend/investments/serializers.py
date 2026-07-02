from rest_framework import serializers
from decimal import Decimal
from .models import InvestmentCategory, InvestmentPlatform, InvestmentSnapshot, Asset, InvestmentSnapshotAsset

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

class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class InvestmentSnapshotAssetSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    category_name = serializers.CharField(source='asset.category.name', read_only=True)
    category_id = serializers.IntegerField(source='asset.category.id', read_only=True)

    class Meta:
        model = InvestmentSnapshotAsset
        fields = ['id', 'asset', 'asset_name', 'category_name', 'category_id', 'weight', 'value']

class InvestmentSnapshotSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    absolute_profit = serializers.SerializerMethodField()
    profit_percentage = serializers.SerializerMethodField()
    snapshot_assets = InvestmentSnapshotAssetSerializer(many=True, required=False)

    class Meta:
        model = InvestmentSnapshot
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'category': {'required': False, 'allow_null': True}
        }

    def get_absolute_profit(self, obj):
        return round(obj.current_balance - obj.total_invested, 2)

    def get_profit_percentage(self, obj):
        if obj.total_invested > 0:
            return round(((obj.current_balance - obj.total_invested) / obj.total_invested) * 100, 2)
        return 0.00

    def create(self, validated_data):
        snapshot_assets_data = validated_data.pop('snapshot_assets', [])
        # Determine category fallback
        platform = validated_data.get('platform')
        category = platform.category if platform else None
        validated_data['category'] = category

        snapshot = InvestmentSnapshot.objects.create(**validated_data)
        self._save_assets(snapshot, snapshot_assets_data)
        return snapshot

    def update(self, instance, validated_data):
        snapshot_assets_data = validated_data.pop('snapshot_assets', None)
        
        # Keep category updated to platform category if present
        platform = validated_data.get('platform', instance.platform)
        if platform:
            validated_data['category'] = platform.category

        instance = super().update(instance, validated_data)

        if snapshot_assets_data is not None:
            instance.snapshot_assets.all().delete()
            self._save_assets(instance, snapshot_assets_data)

        return instance

    def _save_assets(self, snapshot, snapshot_assets_data):
        total_balance = Decimal(str(snapshot.current_balance))
        for asset_data in snapshot_assets_data:
            weight = asset_data.get('weight')
            value = asset_data.get('value')

            # Perform auto-calculation if one of weight or value is provided but the other is not
            if weight is not None and value is None:
                if total_balance > 0:
                    value = (Decimal(str(weight)) / Decimal('100')) * total_balance
                else:
                    value = Decimal('0.00')
            elif value is not None and weight is None:
                if total_balance > 0:
                    weight = (Decimal(str(value)) / total_balance) * Decimal('100')
                else:
                    weight = Decimal('0.00')
            elif weight is None and value is None:
                # Default fallback
                weight = Decimal('0.00')
                value = Decimal('0.00')

            # Round values
            if weight is not None:
                weight = round(Decimal(str(weight)), 2)
            if value is not None:
                value = round(Decimal(str(value)), 2)

            InvestmentSnapshotAsset.objects.create(
                snapshot=snapshot,
                asset=asset_data['asset'],
                weight=weight,
                value=value
            )
