from django.urls import path
from .views import login_usuario, logout_usuario, validar_credenciais, reenviar_codigo_2fa

urlpatterns = [
    path('login/', login_usuario, name='login'),
    path('logout/', logout_usuario, name='logout'),
    path('validar-credenciais/', validar_credenciais, name='validar_credenciais'),
    path('reenviar-2fa/', reenviar_codigo_2fa, name='reenviar_2fa'),
]