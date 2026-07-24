from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, SlaConfigViewSet, TicketViewSet, TicketMessageViewSet

# O DefaultRouter gera automaticamente as rotas GET, POST, PUT, DELETE
router = DefaultRouter()
router.register(r'categorias', CategoryViewSet)
router.register(r'slas', SlaConfigViewSet)
router.register(r'chamados', TicketViewSet)
router.register(r'mensagens', TicketMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]