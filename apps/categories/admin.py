from django.contrib import admin
from .models import Category, WorkArea

class WorkAreaInline(admin.TabularInline):
    model = WorkArea
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_active', 'tarjetas_count', 'open_tarjetas_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    inlines = [WorkAreaInline]
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'tarjetas_count', 'open_tarjetas_count']

@admin.register(WorkArea)
class WorkAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'responsible', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'category__name']