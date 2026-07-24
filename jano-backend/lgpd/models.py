from django.db import models
from django.conf import settings
from django.utils import timezone

class ConsentimentoLGPD(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consentimento')
    
    # Item 4.4: Registro explícito (Sim/Não)
    aceite_termos = models.BooleanField(default=False)
    
    # Item 4.5: Finalidade associada ao dado
    finalidade = models.TextField(
        default="Armazenamento seguro e criptografado de credenciais de terceiros e gerenciamento de acesso."
    )
    
    # Item 4.6: Possibilidade de revogação
    consentimento_ativo = models.BooleanField(default=True)
    data_revogacao = models.DateTimeField(null=True, blank=True)
    
    # Item 4.7: Registro de data e versão
    data_aceite = models.DateTimeField(auto_now_add=True)
    versao_termo = models.CharField(max_length=10, default="1.0")

    def revogar(self):
        self.consentimento_ativo = False
        self.data_revogacao = timezone.now()
        self.save()

    def __str__(self):
        status = "Ativo" if self.consentimento_ativo else "Revogado"
        return f"Consentimento de {self.usuario.email} - {status} (v{self.versao_termo})"