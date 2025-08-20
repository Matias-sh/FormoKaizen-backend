from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, WorkArea
from .serializers import CategorySerializer, CategoryCreateSerializer, WorkAreaSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def categories_list(request):
    if request.method == 'GET':
        categories = Category.objects.filter(is_active=True).prefetch_related('work_areas')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_supervisor():
            return Response({
                'error': 'No tienes permisos para crear categorías'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CategoryCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            category = serializer.save()
            return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk, is_active=True)
    except Category.DoesNotExist:
        return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not request.user.is_supervisor():
            return Response({
                'error': 'No tienes permisos para modificar categorías'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not request.user.is_admin():
            return Response({
                'error': 'Solo los administradores pueden eliminar categorías'
            }, status=status.HTTP_403_FORBIDDEN)
        
        category.is_active = False
        category.save()
        return Response({'message': 'Categoría eliminada exitosamente'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def work_areas_list(request, category_pk):
    try:
        category = Category.objects.get(pk=category_pk, is_active=True)
    except Category.DoesNotExist:
        return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        work_areas = WorkArea.objects.filter(category=category, is_active=True)
        serializer = WorkAreaSerializer(work_areas, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_supervisor():
            return Response({
                'error': 'No tienes permisos para crear áreas de trabajo'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = WorkAreaSerializer(data=request.data)
        if serializer.is_valid():
            work_area = serializer.save(category=category)
            return Response(WorkAreaSerializer(work_area).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)