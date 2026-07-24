from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas base da nossa API
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/recovery/', include('recovery.urls')),
    path('api/v1/lgpd/', include('lgpd.urls')),
]