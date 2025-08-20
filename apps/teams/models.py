from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre del equipo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='led_teams', verbose_name='Líder del equipo')
    members = models.ManyToManyField(User, through='TeamMembership', 
                                    through_fields=('team', 'user'), related_name='teams')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()
    
    @property
    def active_tarjetas_count(self):
        from apps.tarjetas.models import TarjetaRoja
        member_ids = self.memberships.filter(is_active=True).values_list('user_id', flat=True)
        return TarjetaRoja.objects.filter(
            is_active=True,
            assigned_to_id__in=member_ids,
            status__in=['open', 'in_progress', 'approved']
        ).count()

class TeamMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Miembro'),
        ('coordinator', 'Coordinador'),
        ('observer', 'Observador'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='added_memberships')
    
    class Meta:
        db_table = 'team_memberships'
        verbose_name = 'Membresía de Equipo'
        verbose_name_plural = 'Membresías de Equipos'
        unique_together = ['team', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.full_name} en {self.team.name} ({self.role})"

class TeamProject(models.Model):
    """Proyectos específicos de un equipo"""
    name = models.CharField(max_length=200, verbose_name='Nombre del proyecto')
    description = models.TextField(blank=True, verbose_name='Descripción')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='responsible_projects')
    start_date = models.DateField(verbose_name='Fecha de inicio')
    target_end_date = models.DateField(verbose_name='Fecha objetivo de finalización')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='Fecha real de finalización')
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planificación'),
        ('active', 'Activo'),
        ('on_hold', 'En pausa'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ], default='planning')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'team_projects'
        verbose_name = 'Proyecto de Equipo'
        verbose_name_plural = 'Proyectos de Equipos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.team.name}"
    
    @property
    def is_overdue(self):
        if self.status not in ['completed', 'cancelled'] and self.target_end_date:
            from django.utils import timezone
            return timezone.now().date() > self.target_end_date
        return False