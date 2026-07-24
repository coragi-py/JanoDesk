from rest_framework import viewsets, permissions
from .models import Category, SlaConfig, Ticket, TicketMessage
from .serializers import CategorySerializer, SlaConfigSerializer, TicketSerializer, TicketMessageSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated] # Bloqueia acesso anônimo

class SlaConfigViewSet(viewsets.ModelViewSet):
    queryset = SlaConfig.objects.all()
    serializer_class = SlaConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-criado_em')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Quando um chamado é criado, atrela automaticamente ao usuário logado
        serializer.save(solicitante=self.request.user)

class TicketMessageViewSet(viewsets.ModelViewSet):
    queryset = TicketMessage.objects.all().order_by('criado_em')
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Atrela o autor da mensagem ao usuário que disparou a requisição
        serializer.save(autor=self.request.user)