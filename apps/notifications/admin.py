from django.contrib import admin
from .models import Notification, NotificationPreference, DeviceToken

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'priority', 
                   'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at', 'send_email', 'send_push']
    search_fields = ['title', 'message', 'recipient__first_name', 'recipient__last_name', 
                    'recipient__email']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información General', {
            'fields': ('recipient', 'sender', 'notification_type', 'priority')
        }),
        ('Contenido', {
            'fields': ('title', 'message')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at')
        }),
        ('Entrega', {
            'fields': ('send_email', 'email_sent', 'send_push', 'push_sent')
        }),
        ('Objeto Relacionado', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_tarjeta_created', 'push_tarjeta_created', 
                   'weekend_notifications', 'updated_at']
    list_filter = ['weekend_notifications', 'email_tarjeta_created', 'push_tarjeta_created']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'device_name', 'is_active', 'last_used']
    list_filter = ['platform', 'is_active', 'created_at', 'last_used']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'device_name']
    readonly_fields = ['created_at', 'last_used']