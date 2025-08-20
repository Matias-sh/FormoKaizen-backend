from rest_framework import serializers
from .models import TarjetaRoja, TarjetaImage, TarjetaComment, TarjetaHistory
from apps.users.serializers import UserSerializer

class TarjetaImageSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TarjetaImage
        fields = ['id', 'image', 'description', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']

class TarjetaCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TarjetaComment
        fields = ['id', 'comment', 'is_internal', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class TarjetaHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TarjetaHistory
        fields = ['id', 'action', 'old_value', 'new_value', 'user', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']

class TarjetaRojaListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    code = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_open = serializers.ReadOnlyField()
    
    class Meta:
        model = TarjetaRoja
        fields = ['id', 'code', 'numero', 'fecha', 'sector', 'descripcion', 'status', 'priority', 
                 'created_by', 'assigned_to', 'approved_by', 'quien_lo_hizo',
                 'created_at', 'updated_at', 'is_overdue', 'days_open']

class TarjetaRojaDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    images = TarjetaImageSerializer(many=True, read_only=True)
    comments = TarjetaCommentSerializer(many=True, read_only=True)
    history = TarjetaHistorySerializer(many=True, read_only=True)
    code = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_open = serializers.ReadOnlyField()
    
    class Meta:
        model = TarjetaRoja
        fields = ['id', 'code', 'numero', 'fecha', 'sector', 'descripcion',
                 'razon_motivo', 'quien_lo_hizo', 'destino_final', 'fecha_final',
                 'status', 'priority', 'created_by', 'assigned_to', 'approved_by',
                 'resolution_notes', 'images', 'comments', 'history',
                 'created_at', 'updated_at', 'approved_at', 'closed_at',
                 'is_overdue', 'days_open']

class TarjetaRojaCreateSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = TarjetaRoja
        fields = ['numero', 'fecha', 'sector', 'descripcion', 'razon_motivo',
                 'quien_lo_hizo', 'destino_final', 'fecha_final', 'priority',
                 'assigned_to_id']
    
    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        if assigned_to_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                assigned_user = User.objects.get(id=assigned_to_id)
                validated_data['assigned_to'] = assigned_user
            except User.DoesNotExist:
                raise serializers.ValidationError({'assigned_to_id': 'Usuario no encontrado'})
        
        validated_data['created_by'] = self.context['request'].user
        
        # Si el usuario no es supervisor, la tarjeta necesita aprobación
        if not self.context['request'].user.is_supervisor():
            validated_data['status'] = 'pending_approval'
        else:
            validated_data['status'] = 'approved'
            validated_data['approved_by'] = self.context['request'].user
            from django.utils import timezone
            validated_data['approved_at'] = timezone.now()
        
        return super().create(validated_data)

class TarjetaRojaUpdateSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = TarjetaRoja
        fields = ['numero', 'fecha', 'sector', 'descripcion', 'razon_motivo',
                 'quien_lo_hizo', 'destino_final', 'fecha_final', 'priority',
                 'assigned_to_id', 'status', 'resolution_notes']
    
    def update(self, instance, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        if assigned_to_id is not None:
            if assigned_to_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    assigned_user = User.objects.get(id=assigned_to_id)
                    validated_data['assigned_to'] = assigned_user
                except User.DoesNotExist:
                    raise serializers.ValidationError({'assigned_to_id': 'Usuario no encontrado'})
            else:
                validated_data['assigned_to'] = None
        
        # Lógica para cambios de estado
        if 'status' in validated_data:
            new_status = validated_data['status']
            old_status = instance.status
            
            if new_status == 'closed' and old_status != 'closed':
                from django.utils import timezone
                validated_data['closed_at'] = timezone.now()
            elif new_status == 'resolved' and 'fecha_final' not in validated_data:
                from django.utils import timezone
                validated_data['fecha_final'] = timezone.now().date()
        
        return super().update(instance, validated_data)