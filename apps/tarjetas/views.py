from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .models import TarjetaRoja, TarjetaImage, TarjetaComment, TarjetaHistory
from .serializers import (
    TarjetaRojaListSerializer, TarjetaRojaDetailSerializer, 
    TarjetaRojaCreateSerializer, TarjetaRojaUpdateSerializer,
    TarjetaImageSerializer, TarjetaCommentSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tarjetas_list(request):
    if request.method == 'GET':
        queryset = TarjetaRoja.objects.filter(is_active=True).select_related(
            'created_by', 'assigned_to', 'approved_by'
        )
        
        # Filtros
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        sector_filter = request.GET.get('sector')
        if sector_filter:
            queryset = queryset.filter(sector__icontains=sector_filter)
        
        priority_filter = request.GET.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        assigned_to_filter = request.GET.get('assigned_to')
        if assigned_to_filter:
            if assigned_to_filter == 'me':
                queryset = queryset.filter(assigned_to=request.user)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to_filter)
        
        created_by_filter = request.GET.get('created_by')
        if created_by_filter:
            if created_by_filter == 'me':
                queryset = queryset.filter(created_by=request.user)
            else:
                queryset = queryset.filter(created_by_id=created_by_filter)
        
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(sector__icontains=search) |
                Q(quien_lo_hizo__icontains=search)
            )
        
        # Paginación básica
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page
        
        total_count = queryset.count()
        tarjetas = queryset[start:end]
        
        serializer = TarjetaRojaListSerializer(tarjetas, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
    
    elif request.method == 'POST':
        serializer = TarjetaRojaCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tarjeta = serializer.save()
            
            # Crear entrada en el historial
            TarjetaHistory.objects.create(
                tarjeta=tarjeta,
                user=request.user,
                action='created',
                new_value=tarjeta.status
            )
            
            return Response(
                TarjetaRojaDetailSerializer(tarjeta).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def tarjeta_detail(request, pk):
    try:
        tarjeta = TarjetaRoja.objects.select_related(
            'created_by', 'assigned_to', 'approved_by'
        ).prefetch_related(
            'images', 'comments__user', 'history__user'
        ).get(pk=pk, is_active=True)
    except TarjetaRoja.DoesNotExist:
        return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TarjetaRojaDetailSerializer(tarjeta)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not tarjeta.can_be_edited_by(request.user):
            return Response({
                'error': 'No tienes permisos para editar esta tarjeta'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Guardar valores anteriores para el historial
        old_values = {
            'status': tarjeta.status,
            'assigned_to': tarjeta.assigned_to_id,
            'priority': tarjeta.priority
        }
        
        serializer = TarjetaRojaUpdateSerializer(tarjeta, data=request.data, partial=True)
        if serializer.is_valid():
            updated_tarjeta = serializer.save()
            
            # Crear entradas en el historial para cambios importantes
            for field in ['status', 'assigned_to', 'priority']:
                if field in request.data:
                    old_value = old_values[field]
                    if field == 'assigned_to':
                        new_value = request.data.get('assigned_to_id')
                    else:
                        new_value = getattr(updated_tarjeta, field)
                    
                    if old_value != new_value:
                        TarjetaHistory.objects.create(
                            tarjeta=updated_tarjeta,
                            user=request.user,
                            action=f'updated_{field}',
                            old_value=str(old_value) if old_value else '',
                            new_value=str(new_value) if new_value else ''
                        )
            
            return Response(TarjetaRojaDetailSerializer(updated_tarjeta).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_admin() and tarjeta.created_by != request.user:
            return Response({
                'error': 'No tienes permisos para eliminar esta tarjeta'
            }, status=status.HTTP_403_FORBIDDEN)
        
        tarjeta.is_active = False
        tarjeta.save()
        
        TarjetaHistory.objects.create(
            tarjeta=tarjeta,
            user=request.user,
            action='deleted'
        )
        
        return Response({'message': 'Tarjeta eliminada exitosamente'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_tarjeta(request, pk):
    try:
        tarjeta = TarjetaRoja.objects.get(pk=pk, is_active=True)
    except TarjetaRoja.DoesNotExist:
        return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if not tarjeta.can_be_approved_by(request.user):
        return Response({
            'error': 'No puedes aprobar esta tarjeta'
        }, status=status.HTTP_403_FORBIDDEN)
    
    action = request.data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        tarjeta.status = 'approved'
        tarjeta.approved_by = request.user
        tarjeta.approved_at = timezone.now()
        message = 'Tarjeta aprobada exitosamente'
    elif action == 'reject':
        tarjeta.status = 'rejected'
        message = 'Tarjeta rechazada'
    else:
        return Response({'error': 'Acción inválida'}, status=status.HTTP_400_BAD_REQUEST)
    
    tarjeta.save()
    
    # Agregar comentario si se proporciona
    comment_text = request.data.get('comment')
    if comment_text:
        TarjetaComment.objects.create(
            tarjeta=tarjeta,
            user=request.user,
            comment=comment_text,
            is_internal=True
        )
    
    TarjetaHistory.objects.create(
        tarjeta=tarjeta,
        user=request.user,
        action=action,
        new_value=tarjeta.status
    )
    
    return Response({
        'message': message,
        'tarjeta': TarjetaRojaDetailSerializer(tarjeta).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request, pk):
    try:
        tarjeta = TarjetaRoja.objects.get(pk=pk, is_active=True)
    except TarjetaRoja.DoesNotExist:
        return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TarjetaImageSerializer(data=request.data)
    if serializer.is_valid():
        image = serializer.save(tarjeta=tarjeta, uploaded_by=request.user)
        return Response(TarjetaImageSerializer(image).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, pk):
    try:
        tarjeta = TarjetaRoja.objects.get(pk=pk, is_active=True)
    except TarjetaRoja.DoesNotExist:
        return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TarjetaCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(tarjeta=tarjeta, user=request.user)
        return Response(TarjetaCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    if not request.user.is_supervisor():
        return Response({
            'error': 'No tienes permisos para ver estadísticas'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Estadísticas generales
    total_tarjetas = TarjetaRoja.objects.filter(is_active=True).count()
    open_tarjetas = TarjetaRoja.objects.filter(is_active=True, status='open').count()
    pending_approval = TarjetaRoja.objects.filter(is_active=True, status='pending_approval').count()
    in_progress = TarjetaRoja.objects.filter(is_active=True, status='in_progress').count()
    resolved = TarjetaRoja.objects.filter(is_active=True, status='resolved').count()
    overdue = TarjetaRoja.objects.filter(is_active=True).filter(
        fecha_final__lt=timezone.now().date(),
        status__in=['open', 'in_progress', 'approved']
    ).count()
    
    # Estadísticas por prioridad
    priority_stats = {}
    for priority, _ in TarjetaRoja.PRIORITY_CHOICES:
        priority_stats[priority] = TarjetaRoja.objects.filter(
            is_active=True, priority=priority
        ).count()
    
    # Estadísticas por sector
    from django.db.models import Count
    sector_stats = TarjetaRoja.objects.filter(is_active=True).values('sector').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    return Response({
        'total_tarjetas': total_tarjetas,
        'status_stats': {
            'open': open_tarjetas,
            'pending_approval': pending_approval,
            'in_progress': in_progress,
            'resolved': resolved,
            'overdue': overdue
        },
        'priority_stats': priority_stats,
        'sector_stats': list(sector_stats)
    })