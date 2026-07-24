from django.urls import path
from .views import aceitar_termos_novamente, privacidade_dashboard, revogar_consentimento, consultar_meus_dados, exportar_meus_dados, excluir_minha_conta

urlpatterns = [
    path('', privacidade_dashboard, name='privacidade_dashboard'),
    path('revogar/', revogar_consentimento, name='revogar_consentimento'),
    path('consultar/', consultar_meus_dados, name='consultar_meus_dados'),
    path('exportar/', exportar_meus_dados, name='exportar_meus_dados'),
    path('excluir/', excluir_minha_conta, name='excluir_minha_conta'),
    path('reativar/', aceitar_termos_novamente, name='aceitar_termos_novamente'),
]