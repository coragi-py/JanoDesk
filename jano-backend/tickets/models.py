import uuid
from django.db import models
from django.conf import settings
from audit.models import AuditLog
from django_cryptography.fields import encrypt

class Category(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.nome

class SlaConfig(models.Model):
    PRIORITY_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente (Crítico)'),
    ]
    prioridade = models.CharField(max_length=20, choices=PRIORITY_CHOICES, unique=True)
    tempo_resposta_horas = models.IntegerField(help_text="Tempo máximo para o primeiro atendimento")
    tempo_resolucao_horas = models.IntegerField(help_text="Tempo máximo para resolver o chamado")

    def __str__(self):
        return f"SLA - {self.get_prioridade_display()}"

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('AGUARDANDO_USUARIO', 'Aguardando Usuário'),
        ('RESOLVIDO', 'Resolvido'),
        ('FECHADO', 'Fechado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=200)
    
    # === PSEUDONIMIZAÇÃO ===
    # O texto fica ilegível no banco, mas a API lê normalmente usando a SECRET_KEY
    descricao = encrypt(models.TextField(help_text="Descreva o problema detalhadamente."))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO')
    
    categoria = models.ForeignKey(Category, on_delete=models.PROTECT)
    sla = models.ForeignKey(SlaConfig, on_delete=models.PROTECT, null=True, blank=True)
    
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chamados_abertos', on_delete=models.SET_NULL, null=True)
    tecnico_atribuido = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chamados_atendidos', on_delete=models.SET_NULL, null=True, blank=True)
    
    asset = models.ForeignKey('assets.Asset', on_delete=models.SET_NULL, null=True, blank=True, help_text="Equipamento relacionado")
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def anonimizar_dados_lgpd(self):
        """
        Direito ao Esquecimento: Destrói permanentemente a informação,
        sobrepondo o dado pseudonimizado com um texto padrão.
        """
        self.titulo = f"[ANONIMIZADO] Ticket {self.id}"
        self.descricao = "[CONTEÚDO REMOVIDO E ANONIMIZADO PARA CONFORMIDADE LGPD]"
        self.save()
        AuditLog.objects.create(
            usuario=None, 
            acao="ANONIMIZACAO_LGPD", 
            ip_address="0.0.0.0", 
            detalhes=f"Ticket {self.id} anonimizado a pedido do titular."
        )

    def __str__(self):
        return f"[{self.status}] {self.titulo}"

class TicketMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, related_name='mensagens', on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # === PSEUDONIMIZAÇÃO ===
    mensagem = encrypt(models.TextField())
    
    is_internal = models.BooleanField(default=False, help_text="Apenas técnicos podem ver?")
    criado_em = models.DateTimeField(auto_now_add=True)

    def anonimizar_mensagem_lgpd(self):
        self.mensagem = "[MENSAGEM APAGADA VIA LGPD]"
        self.save()

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='anexos', on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='chamados_anexos/%Y/%m/')
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    enviado_em = models.DateTimeField(auto_now_add=True)