from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    path('register-device/', views.register_device_token, name='register_device_token'),
    path('create/', views.create_notification, name='create_notification'),
    path('stats/', views.notification_stats, name='notification_stats'),
]