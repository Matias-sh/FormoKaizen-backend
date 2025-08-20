from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'role', 'department', 'is_active', 'created_at']
    list_filter = ['role', 'department', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'employee_id']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('role', 'employee_id', 'phone', 'department', 'position', 'avatar')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'role', 'employee_id', 'phone', 'department', 'position')
        }),
    )