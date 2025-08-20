from django.urls import path
from . import views

urlpatterns = [
    path('', views.categories_list, name='categories_list'),
    path('<int:pk>/', views.category_detail, name='category_detail'),
    path('<int:category_pk>/work-areas/', views.work_areas_list, name='work_areas_list'),
]