import random
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class EmailToken2FA(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_tokens')
    codigo = models.CharField(max_length=6) # Token numérico de 6 dígitos
    criado_em = models.DateTimeField(auto_now_add=True)
    utilizado = models.BooleanField(default=False)
    tentativas = models.IntegerField(default=0) # Organizado junto com os outros campos

    def __str__(self):
        return f"Token para {self.user.email} - {self.codigo}"

    @property
    def expirou(self):
        # Valida expiração em 15 minutos
        return timezone.now() > self.criado_em + timedelta(minutes=15)

    # CORRIGIDO: Agora esta função está devidamente recuada para dentro da classe
    def validar_token(self, codigo_informado):
        if self.utilizado:
            return False, "Este token já foi utilizado."
        if self.expirou:
            return False, "Este token expirou (validade de 15 minutos)."
        
        # 1. Incrementa o contador de tentativas a cada checagem
        self.tentativas += 1
        self.save()

        # 2. Defesa contra Brute Force, limite de 5 tentativas antes de descartar o codigo
        if self.tentativas > 5:
            self.utilizado = True
            self.save()
            return False, "Número máximo de tentativas excedido. Solicite um novo código."

        # 3. Valida o código
        if self.codigo != codigo_informado:
            tentativas_restantes = 5 - self.tentativas
            return False, f"Código incorreto. Você tem mais {tentativas_restantes} tentativa(s)."
        
        # Sucesso: Descarta o token para uso único
        self.utilizado = True
        self.save()
        return True, "Token validado com sucesso."