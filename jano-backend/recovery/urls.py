from django.urls import path
from .views import solicitar_recuperacao, resetar_senha

urlpatterns = [
    # Rota para gerar o token: /recovery/request/
    path('request/', solicitar_recuperacao, name='solicitar_recuperacao'),
    
    # Rota para redefinir a senha: /recovery/reset/
    path('reset/', resetar_senha, name='resetar_senha'),
]