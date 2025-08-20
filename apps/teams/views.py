from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Team, TeamMembership, TeamProject
from .serializers import (
    TeamListSerializer, TeamDetailSerializer, TeamCreateSerializer,
    TeamMembershipSerializer, TeamProjectSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teams_list(request):
    if request.method == 'GET':
        # Los usuarios regulares solo ven sus equipos
        if request.user.is_supervisor():
            teams = Team.objects.filter(is_active=True).prefetch_related('memberships__user')
        else:
            teams = Team.objects.filter(
                is_active=True,
                memberships__user=request.user,
                memberships__is_active=True
            ).prefetch_related('memberships__user')
        
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_supervisor():
            return Response({
                'error': 'No tienes permisos para crear equipos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TeamCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            team = serializer.save()
            return Response(TeamDetailSerializer(team).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def team_detail(request, pk):
    try:
        team = Team.objects.prefetch_related(
            'memberships__user', 'projects'
        ).get(pk=pk, is_active=True)
    except Team.DoesNotExist:
        return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar permisos: supervisores o miembros del equipo
    if not request.user.is_supervisor():
        is_member = team.memberships.filter(
            user=request.user, is_active=True
        ).exists()
        if not is_member:
            return Response({
                'error': 'No tienes permisos para ver este equipo'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = TeamDetailSerializer(team)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_supervisor():
            return Response({
                'error': 'No tienes permisos para modificar equipos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TeamDetailSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_admin():
            return Response({
                'error': 'Solo los administradores pueden eliminar equipos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        team.is_active = False
        team.save()
        return Response({'message': 'Equipo eliminado exitosamente'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_team_member(request, pk):
    try:
        team = Team.objects.get(pk=pk, is_active=True)
    except Team.DoesNotExist:
        return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if not request.user.is_supervisor() and team.leader != request.user:
        return Response({
            'error': 'No tienes permisos para agregar miembros a este equipo'
        }, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    role = request.data.get('role', 'member')
    
    if not user_id:
        return Response({'error': 'user_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar si ya es miembro activo
    existing_membership = TeamMembership.objects.filter(
        team=team, user=user, is_active=True
    ).first()
    
    if existing_membership:
        return Response({
            'error': 'El usuario ya es miembro de este equipo'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear o reactivar membresía
    membership, created = TeamMembership.objects.get_or_create(
        team=team,
        user=user,
        defaults={
            'role': role,
            'added_by': request.user,
            'is_active': True
        }
    )
    
    if not created:
        membership.is_active = True
        membership.role = role
        membership.left_at = None
        membership.save()
    
    serializer = TeamMembershipSerializer(membership)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def team_member_detail(request, pk, member_pk):
    try:
        team = Team.objects.get(pk=pk, is_active=True)
        membership = TeamMembership.objects.get(pk=member_pk, team=team)
    except (Team.DoesNotExist, TeamMembership.DoesNotExist):
        return Response({'error': 'Membresía no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if not request.user.is_supervisor() and team.leader != request.user:
        return Response({
            'error': 'No tienes permisos para modificar miembros de este equipo'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        new_role = request.data.get('role')
        if new_role and new_role in dict(TeamMembership.ROLE_CHOICES):
            membership.role = new_role
            membership.save()
            return Response(TeamMembershipSerializer(membership).data)
        return Response({'error': 'Rol inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        membership.is_active = False
        membership.left_at = timezone.now()
        membership.save()
        return Response({'message': 'Miembro removido del equipo'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def team_projects(request, pk):
    try:
        team = Team.objects.get(pk=pk, is_active=True)
    except Team.DoesNotExist:
        return Response({'error': 'Equipo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar permisos: supervisores o miembros del equipo
    if not request.user.is_supervisor():
        is_member = team.memberships.filter(
            user=request.user, is_active=True
        ).exists()
        if not is_member:
            return Response({
                'error': 'No tienes permisos para ver proyectos de este equipo'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        projects = team.projects.filter(is_active=True)
        serializer = TeamProjectSerializer(projects, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_supervisor() and team.leader != request.user:
            return Response({
                'error': 'No tienes permisos para crear proyectos en este equipo'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TeamProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(team=team)
            return Response(TeamProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)