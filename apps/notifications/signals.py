from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Notification, NotificationPreference

@receiver(post_save, sender='tarjetas.TarjetaRoja')
def create_tarjeta_notifications(sender, instance, created, **kwargs):
    """Crear notificaciones automáticas para eventos de tarjetas rojas"""
    if created:
        # Notificación para supervisores cuando se crea una nueva tarjeta
        from apps.users.models import User
        supervisors = User.objects.filter(role__in=['admin', 'supervisor'])
        
        for supervisor in supervisors:
            Notification.objects.create(
                recipient=supervisor,
                sender=instance.created_by,
                notification_type='tarjeta_created',
                title=f'Nueva Tarjeta Roja: {instance.code}',
                message=f'{instance.created_by.full_name} ha creado una nueva tarjeta roja: {instance.descripcion[:50]}{"..." if len(instance.descripcion) > 50 else ""}',
                content_object=instance,
                priority='normal' if instance.priority == 'low' else 'high'
            )
    
    else:  # Tarjeta actualizada
        # Verificar cambios de estado
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            
            # Si cambió el estado
            if hasattr(old_instance, 'status') and old_instance.status != instance.status:
                if instance.status == 'approved':
                    # Notificar al creador que su tarjeta fue aprobada
                    Notification.objects.create(
                        recipient=instance.created_by,
                        sender=instance.approved_by,
                        notification_type='tarjeta_approved',
                        title=f'Tarjeta Aprobada: {instance.code}',
                        message=f'Tu tarjeta roja ha sido aprobada por {instance.approved_by.full_name}',
                        content_object=instance,
                        priority='normal'
                    )
                
                elif instance.status == 'rejected':
                    # Notificar al creador que su tarjeta fue rechazada
                    Notification.objects.create(
                        recipient=instance.created_by,
                        notification_type='tarjeta_rejected',
                        title=f'Tarjeta Rechazada: {instance.code}',
                        message=f'Tu tarjeta roja ha sido rechazada. Por favor revisa los comentarios.',
                        content_object=instance,
                        priority='high'
                    )
            
            # Si cambió la asignación
            if hasattr(old_instance, 'assigned_to') and old_instance.assigned_to != instance.assigned_to:
                if instance.assigned_to:
                    Notification.objects.create(
                        recipient=instance.assigned_to,
                        sender=instance.created_by,
                        notification_type='tarjeta_assigned',
                        title=f'Tarjeta Asignada: {instance.code}',
                        message=f'Te han asignado una tarjeta roja: {instance.descripcion[:50]}{"..." if len(instance.descripcion) > 50 else ""}',
                        content_object=instance,
                        priority='high' if instance.priority in ['high', 'critical'] else 'normal'
                    )
        
        except sender.DoesNotExist:
            pass  # Ignorar si no se puede obtener la instancia anterior

@receiver(post_save, sender='tarjetas.TarjetaComment')
def create_comment_notifications(sender, instance, created, **kwargs):
    """Notificaciones para nuevos comentarios"""
    if created:
        # Notificar al creador de la tarjeta y al asignado (si no es quien comentó)
        recipients = []
        
        if instance.tarjeta.created_by != instance.user:
            recipients.append(instance.tarjeta.created_by)
        
        if instance.tarjeta.assigned_to and instance.tarjeta.assigned_to != instance.user:
            recipients.append(instance.tarjeta.assigned_to)
        
        for recipient in recipients:
            # Verificar preferencias del usuario
            preferences, _ = NotificationPreference.objects.get_or_create(user=recipient)
            
            if not instance.is_internal or recipient.is_supervisor():
                Notification.objects.create(
                    recipient=recipient,
                    sender=instance.user,
                    notification_type='comment_added',
                    title=f'Nuevo comentario en {instance.tarjeta.code}',
                    message=f'{instance.user.full_name} ha agregado un comentario',
                    content_object=instance.tarjeta,
                    priority='normal',
                    send_email=preferences.email_comment_added,
                    send_push=preferences.push_comment_added
                )

@receiver(post_save, sender='teams.TeamMembership')
def create_team_notifications(sender, instance, created, **kwargs):
    """Notificaciones para cambios en equipos"""
    if created and instance.is_active:
        # Notificar al usuario que fue agregado al equipo
        Notification.objects.create(
            recipient=instance.user,
            sender=instance.added_by,
            notification_type='team_added',
            title=f'Agregado al equipo: {instance.team.name}',
            message=f'Has sido agregado al equipo {instance.team.name} como {instance.get_role_display()}',
            content_object=instance.team,
            priority='normal'
        )
    
    elif not created and not instance.is_active:
        # Notificar cuando es removido del equipo
        Notification.objects.create(
            recipient=instance.user,
            notification_type='team_removed',
            title=f'Removido del equipo: {instance.team.name}',
            message=f'Has sido removido del equipo {instance.team.name}',
            content_object=instance.team,
            priority='normal'
        )

@receiver(post_save, sender='users.User')
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """Crear preferencias de notificación para nuevos usuarios"""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)