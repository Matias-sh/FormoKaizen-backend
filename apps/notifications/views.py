from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .models import Notification, NotificationPreference, DeviceToken
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer,
    DeviceTokenSerializer, CreateNotificationSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    queryset = Notification.objects.filter(recipient=request.user).select_related('sender')
    
    # Filtros
    unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
    if unread_only:
        queryset = queryset.filter(is_read=False)
    
    notification_type = request.GET.get('type')
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)
    
    priority = request.GET.get('priority')
    if priority:
        queryset = queryset.filter(priority=priority)
    
    # Paginación
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 50))
    start = (page - 1) * per_page
    end = start + per_page
    
    total_count = queryset.count()
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    notifications = queryset[start:end]
    
    serializer = NotificationSerializer(notifications, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'unread_count': unread_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notificación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    notification.mark_as_read()
    return Response({'message': 'Notificación marcada como leída'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    updated_count = Notification.objects.filter(
        recipient=request.user, 
        is_read=False
    ).update(
        is_read=True, 
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'{updated_count} notificaciones marcadas como leídas'
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notificación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    notification.delete()
    return Response({'message': 'Notificación eliminada'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all_notifications(request):
    deleted_count = Notification.objects.filter(recipient=request.user).count()
    Notification.objects.filter(recipient=request.user).delete()
    
    return Response({
        'message': f'{deleted_count} notificaciones eliminadas'
    })

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'GET':
        serializer = NotificationPreferenceSerializer(preferences)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = NotificationPreferenceSerializer(
            preferences, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device_token(request):
    serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        token = serializer.save()
        return Response(DeviceTokenSerializer(token).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_notification(request):
    """Endpoint para crear notificaciones (solo para supervisores)"""
    if not request.user.is_supervisor():
        return Response({
            'error': 'No tienes permisos para crear notificaciones'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CreateNotificationSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        recipients = User.objects.filter(id__in=data['recipient_ids'])
        notifications_created = []
        
        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type=data['notification_type'],
                title=data['title'],
                message=data['message'],
                priority=data['priority'],
                send_email=data['send_email'],
                send_push=data['send_push']
            )
            notifications_created.append(notification)
        
        # TODO: Aquí se enviarían las notificaciones push y email
        
        return Response({
            'message': f'{len(notifications_created)} notificaciones creadas',
            'notifications': NotificationSerializer(notifications_created, many=True).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """Estadísticas de notificaciones para el usuario actual"""
    total = Notification.objects.filter(recipient=request.user).count()
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    # Notificaciones por tipo (últimos 30 días)
    from datetime import datetime, timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    type_stats = {}
    for notification_type, _ in Notification.TYPE_CHOICES:
        count = Notification.objects.filter(
            recipient=request.user,
            notification_type=notification_type,
            created_at__gte=thirty_days_ago
        ).count()
        if count > 0:
            type_stats[notification_type] = count
    
    return Response({
        'total': total,
        'unread': unread,
        'read': total - unread,
        'type_stats_30_days': type_stats
    })