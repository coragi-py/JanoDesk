import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailToken2FA

def verificar_cooldown_reenvio(user):
    """
    Verifica se o usuário respeitou o intervalo de 30 segundos 
    desde a geração do último token.
    Retorna (True, 0) se puder enviar, ou (False, segundos_restantes) se estiver bloqueado.
    """
    # Procura o último token gerado para este usuário (independente de estar ativo ou não)
    ultimo_token = EmailToken2FA.objects.filter(user=user).last()
    
    if ultimo_token:
        agora = timezone.now()
        tempo_decorrido = agora - ultimo_token.criado_em
        cooldown = timedelta(seconds=30)
        
        # Se o tempo decorrido for menor que 30 segundos, bloqueia
        if tempo_decorrido < cooldown:
            segundos_restantes = 30 - int(tempo_decorrido.total_seconds())
            return False, segundos_restantes
            
    return True, 0

def gerar_e_enviar_token_email(user):
    """
    Gera um código numérico de 6 dígitos, invalida tokens anteriores do usuário,
    salva o novo token no banco de dados e envia para o e-mail cadastrado via Brevo.
    """
    # Inativa tokens ativos anteriores do mesmo usuário
    EmailToken2FA.objects.filter(user=user, utilizado=False).update(utilizado=True)
    
    # 2. Gera um token numérico aleatório de 6 dígitos
    novo_codigo = "".join(secrets.choice("0123456789") for _ in range(6))
    
    # 3. Salva no banco de dados relacional (vinculado ao objeto do usuário)
    EmailToken2FA.objects.create(user=user, codigo=novo_codigo)
    
    # 4. Monta e envia o e-mail utilizando a Brevo
    assunto = "Código de Autenticação (2FA) - GSencript"
    mensagem = f"""
    Olá, {user.username}.
    
    Seu código de verificação é:
    
    --> {novo_codigo} <--
    
    Atenção: Este código é de uso único e expira em exatamente 15 minutos.
    Se não foi você quem solicitou este acesso, por favor altere sua senha imediatamente.
    """
    
    # Dispara usando as variáveis que você configurou com sucesso
    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )