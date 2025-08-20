from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    color = models.CharField(max_length=7, default='#0066cc', verbose_name='Color')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icono')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='created_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def tarjetas_count(self):
        return self.tarjetas.filter(is_active=True).count()
    
    @property
    def open_tarjetas_count(self):
        return self.tarjetas.filter(
            is_active=True, 
            status__in=['open', 'in_progress']
        ).count()

class WorkArea(models.Model):
    """Áreas específicas dentro de cada categoría"""
    name = models.CharField(max_length=100, verbose_name='Nombre del área')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='work_areas')
    description = models.TextField(blank=True, verbose_name='Descripción')
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='responsible_areas', 
                                  verbose_name='Responsable')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'work_areas'
        verbose_name = 'Área de Trabajo'
        verbose_name_plural = 'Áreas de Trabajo'
        unique_together = ['name', 'category']
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"