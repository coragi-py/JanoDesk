from django.db import models
from django.conf import settings
from django.core.exceptions import PermissionDenied

class AuditLog(models.Model):
    EVENTO_CHOICES = [
        ('CADASTRO', 'Cadastro de Usuário'),
        ('LOGIN_SUCESSO', 'Sucesso no Login'),
        ('LOGIN_FALHA', 'Falha no Login'),
        ('LOGOUT', 'Logout do Sistema'),
        ('BLOQUEIO_FORCA_BRUTA', 'Bloqueio por Força Bruta'),
        ('RECUPERACAO_SOLICITADA', 'Recuperação de Senha Iniciada'),
        ('RECUPERACAO_SUCESSO', 'Senha Redefinida'),
        ('CRIACAO_SENHA_COFRE', 'Nova Senha no Cofre'),
        ('ALTERACAO_SENHA_COFRE', 'Senha Alterada no Cofre'), 
        ('EXCLUSAO_SENHA_COFRE', 'Senha Excluída do Cofre'),  
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    evento = models.CharField(max_length=50, choices=EVENTO_CHOICES)
    ip_origem = models.GenericIPAddressField(null=True, blank=True)
    detalhes = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        """Impede o UPDATE de registros existentes (WORM)."""
        if self.pk is not None:
            # Se o log já tem um ID, significa que alguém está tentando alterá-lo.
            raise PermissionDenied("Segurança (WORM): Logs de auditoria são inalteráveis. A modificação deste registro foi bloqueada.")
        
        # Se não tem ID, é um log novo, então o sistema permite salvar.
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Impede o DELETE de registros."""
        raise PermissionDenied("Segurança (WORM): O sistema proíbe estritamente a exclusão de registros de auditoria.")

    def __str__(self):
        return f"{self.evento} - {self.usuario if self.usuario else 'Anônimo'} - {self.timestamp}"