from rest_framework import serializers
from .models import Notification, NotificationPreference, DeviceToken
from apps.users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content_object_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'priority',
                 'sender', 'content_object_data', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']
    
    def get_content_object_data(self, obj):
        if obj.content_object:
            if hasattr(obj.content_object, 'id'):
                return {
                    'id': obj.content_object.id,
                    'type': obj.content_type.model,
                    'str': str(obj.content_object)
                }
        return None

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        exclude = ['id', 'user', 'created_at', 'updated_at']

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['token', 'platform', 'device_name']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Desactivar tokens antiguos del mismo usuario y plataforma
        DeviceToken.objects.filter(
            user=validated_data['user'],
            platform=validated_data['platform']
        ).update(is_active=False)
        
        # Crear nuevo token
        return DeviceToken.objects.create(**validated_data)

class CreateNotificationSerializer(serializers.Serializer):
    """Para crear notificaciones desde el admin o sistema"""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de usuarios destinatarios"
    )
    notification_type = serializers.ChoiceField(choices=Notification.TYPE_CHOICES)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, default='normal')
    send_email = serializers.BooleanField(default=False)
    send_push = serializers.BooleanField(default=True)