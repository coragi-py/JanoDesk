import uuid
from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt

class Asset(models.Model):
    TIPO_CHOICES = [
        ('NOTEBOOK', 'Notebook'),
        ('DESKTOP', 'Desktop'),
        ('SERVIDOR', 'Servidor / Cloud'),
        ('IMPRESSORA', 'Impressora'),
        ('REDE', 'Equipamento de Rede (Switch/Roteador)'),
        ('OUTRO', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('ATIVO', 'Em Uso / Ativo'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('ESTOQUE', 'Disponível em Estoque'),
        ('BAIXADO', 'Descartado / Baixado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_patrimonio = models.CharField(max_length=50, unique=True, help_text="Número de série ou etiqueta de patrimônio")
    nome = models.CharField(max_length=150, help_text="Nome identificador do ativo (ex: NB-FIN-01)")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='NOTEBOOK')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO')
    
    # Especificações protegidas por pseudonimização/criptografia (LGPD/Segurança)
    localizacao = encrypt(models.CharField(max_length=200, blank=True, null=True, help_text="Setor ou endereço físico"))
    
    # Atribuição opcional a um usuário responsável
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ativos_atribuidos'
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo_patrimonio} - {self.nome} ({self.get_tipo_display()})"