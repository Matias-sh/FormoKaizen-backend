from django.urls import path
from . import views

urlpatterns = [
    path('', views.teams_list, name='teams_list'),
    path('<int:pk>/', views.team_detail, name='team_detail'),
    path('<int:pk>/add-member/', views.add_team_member, name='add_team_member'),
    path('<int:pk>/members/<int:member_pk>/', views.team_member_detail, name='team_member_detail'),
    path('<int:pk>/projects/', views.team_projects, name='team_projects'),
]