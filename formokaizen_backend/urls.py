from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/tarjetas/', include('apps.tarjetas.urls')),
    path('api/teams/', include('apps.teams.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "FormoKaizen Admin"
admin.site.site_title = "FormoKaizen"
admin.site.index_title = "Gestión de Tarjetas Rojas"