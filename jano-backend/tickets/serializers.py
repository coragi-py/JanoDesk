from rest_framework import serializers
from .models import Category, SlaConfig, Ticket, TicketMessage, TicketAttachment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SlaConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlaConfig
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    # Campos aninhados para leitura amigável no Frontend
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    solicitante_nome = serializers.CharField(source='solicitante.username', read_only=True)
    tecnico_nome = serializers.CharField(source='tecnico_atribuido.username', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'titulo', 'descricao', 'status', 
            'categoria', 'categoria_nome', 'sla', 
            'solicitante', 'solicitante_nome', 'tecnico_atribuido', 'tecnico_nome',
            'asset', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

class TicketMessageSerializer(serializers.ModelSerializer):
    autor_nome = serializers.CharField(source='autor.username', read_only=True)

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'autor', 'autor_nome', 'mensagem', 'is_internal', 'criado_em']
        read_only_fields = ['id', 'criado_em']