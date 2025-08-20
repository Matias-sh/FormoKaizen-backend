from rest_framework import serializers
from .models import Category, WorkArea
from apps.users.serializers import UserSerializer

class WorkAreaSerializer(serializers.ModelSerializer):
    responsible = UserSerializer(read_only=True)
    responsible_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = WorkArea
        fields = ['id', 'name', 'description', 'responsible', 'responsible_id', 
                 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    work_areas = WorkAreaSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    tarjetas_count = serializers.ReadOnlyField()
    open_tarjetas_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'is_active', 
                 'work_areas', 'created_by', 'created_at', 'updated_at',
                 'tarjetas_count', 'open_tarjetas_count']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)