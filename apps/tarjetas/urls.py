from django.urls import path
from . import views

urlpatterns = [
    path('', views.tarjetas_list, name='tarjetas_list'),
    path('<int:pk>/', views.tarjeta_detail, name='tarjeta_detail'),
    path('<int:pk>/approve/', views.approve_tarjeta, name='approve_tarjeta'),
    path('<int:pk>/upload-image/', views.upload_image, name='upload_image'),
    path('<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
]