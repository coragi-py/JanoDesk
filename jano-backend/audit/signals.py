from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from axes.signals import user_locked_out
from accounts.models import User
from .models import AuditLog

# Log de Cadastro
@receiver(post_save, sender=User)
def log_criacao_usuario(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            usuario=instance,
            evento="CADASTRO",
            detalhes=f"Novo usuário registrado: {instance.username}. Consentimento LGPD confirmado."
        )

# Log de Sucesso no Login item 5.1
@receiver(user_logged_in)
def log_login_sucesso(sender, request, user, **kwargs):
    AuditLog.objects.create(
        usuario=user,
        evento="LOGIN_SUCESSO",
        ip_origem=request.META.get('REMOTE_ADDR'),
        detalhes="Autenticação realizada com sucesso."
    )

# Log de Falha no Login item 5.2
@receiver(user_login_failed)
def log_login_falha(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        usuario=None,
        evento="LOGIN_FALHA",
        ip_origem=request.META.get('REMOTE_ADDR'),
        detalhes=f"Tentativa de login inválida para o usuário: {credentials.get('username')}"
    )

# Log de Força Bruta / Bloqueio item 1.11 e 5.2
@receiver(user_locked_out)
def log_bloqueio_axes(sender, request, username, ip_address, **kwargs):
    user = User.objects.filter(username=username).first()
    AuditLog.objects.create(
        usuario=user,
        evento="BLOQUEIO_FORCA_BRUTA",
        ip_origem=ip_address,
        detalhes=f"Conta bloqueada temporariamente após excesso de tentativas falhas."
    )

# Log de encerramento de sessão item 5.1
@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            usuario=user,
            evento="LOGOUT",
            ip_origem=request.META.get('REMOTE_ADDR'),
            detalhes="Sessão encerrada voluntariamente pelo usuário."
        )
