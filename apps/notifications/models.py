from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class Notification(models.Model):
    TYPE_CHOICES = [
        ('tarjeta_created', 'Nueva Tarjeta Roja'),
        ('tarjeta_assigned', 'Tarjeta Asignada'),
        ('tarjeta_approved', 'Tarjeta Aprobada'),
        ('tarjeta_rejected', 'Tarjeta Rechazada'),
        ('tarjeta_completed', 'Tarjeta Completada'),
        ('tarjeta_overdue', 'Tarjeta Vencida'),
        ('comment_added', 'Nuevo Comentario'),
        ('team_added', 'Agregado a Equipo'),
        ('team_removed', 'Removido de Equipo'),
        ('project_assigned', 'Proyecto Asignado'),
        ('system_update', 'Actualización del Sistema'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, 
                                 related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='sent_notifications')
    
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Relación genérica para asociar con cualquier modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                    null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Configuración de entrega
    send_email = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    push_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} -> {self.recipient.full_name}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save()

class NotificationPreference(models.Model):
    """Preferencias de notificación por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                               related_name='notification_preferences')
    
    # Notificaciones por email
    email_tarjeta_created = models.BooleanField(default=True)
    email_tarjeta_assigned = models.BooleanField(default=True)
    email_tarjeta_approved = models.BooleanField(default=True)
    email_tarjeta_overdue = models.BooleanField(default=True)
    email_comment_added = models.BooleanField(default=False)
    email_team_changes = models.BooleanField(default=True)
    
    # Notificaciones push
    push_tarjeta_created = models.BooleanField(default=True)
    push_tarjeta_assigned = models.BooleanField(default=True)
    push_tarjeta_approved = models.BooleanField(default=True)
    push_tarjeta_overdue = models.BooleanField(default=True)
    push_comment_added = models.BooleanField(default=True)
    push_team_changes = models.BooleanField(default=True)
    
    # Configuración general
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    weekend_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Preferencia de Notificación'
        verbose_name_plural = 'Preferencias de Notificaciones'
    
    def __str__(self):
        return f"Preferencias de {self.user.full_name}"

class DeviceToken(models.Model):
    """Tokens de dispositivos para push notifications"""
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=500, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    device_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'device_tokens'
        verbose_name = 'Token de Dispositivo'
        verbose_name_plural = 'Tokens de Dispositivos'
        unique_together = ['user', 'token']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.platform} - {self.device_name}"