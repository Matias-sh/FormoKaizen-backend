from django.contrib import admin
from .models import Team, TeamMembership, TeamProject

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    readonly_fields = ['joined_at', 'added_by']

class TeamProjectInline(admin.TabularInline):
    model = TeamProject
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'member_count', 'active_tarjetas_count', 
                   'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'member_count', 
                      'active_tarjetas_count']
    inlines = [TeamMembershipInline, TeamProjectInline]

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at', 'team']
    search_fields = ['team__name', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['joined_at', 'added_by']

@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'responsible', 'status', 'start_date', 
                   'target_end_date', 'is_overdue']
    list_filter = ['status', 'team', 'start_date', 'target_end_date']
    search_fields = ['name', 'description', 'team__name']
    readonly_fields = ['created_at', 'is_overdue']