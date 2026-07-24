from django.db import models
from django.contrib.auth.models import AbstractUser
from django_cryptography.fields import encrypt

class User(AbstractUser):
    # Tokens sensíveis pseudonimizados (Criptografia em repouso)
    two_factor_secret = encrypt(models.CharField(max_length=32, blank=True, null=True))
    consentimento_lgpd = models.BooleanField(default=False)
    
    # Campos para recuperação de senha pseudonimizados
    recovery_token = encrypt(models.CharField(max_length=64, blank=True, null=True))
    token_expiration = models.DateTimeField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        """
        Design Pattern: Override / Cascata de Anonimização (LGPD)
        Garante que, antes do usuário ser deletado, todos os tickets 
        abertos por ele sejam anonimizados para preservar as métricas da empresa.
        """
        # Verifica se o usuário possui chamados atrelados a ele
        if hasattr(self, 'chamados_abertos'):
            for ticket in self.chamados_abertos.all():
                ticket.anonimizar_dados_lgpd()
        
        # Prossegue com a exclusão física do usuário (apagando PII como Nome e E-mail)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.email