import json
import secrets
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from audit.models import AuditLog

@csrf_exempt
def solicitar_recuperacao(request):
    # Entrega a página HTML caso seja acessado via navegador (GET)
    if request.method == 'GET':
        return render(request, 'recovery/solicitar.html')
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            user = User.objects.filter(email=email).first()
            
            if user:
                # Gera o token de 32 bytes seguro e define expiração (15 minutos)
                user.recovery_token = secrets.token_urlsafe(32)
                user.token_expiration = timezone.now() + timezone.timedelta(minutes=15)
                user.save()
                
                # Monta a URL de redefinição apontando para a sua rota do frontend
                # Em produção, substitua http://127.0.0.1:8000 pelo seu domínio
                url_redefinicao = f"http://127.0.0.1:8000/recovery/reset/?token={user.recovery_token}"
                
                # Corpo do e-mail com instruções claras ao titular dos dados (LGPD)
                assunto = "Recuperação de Acesso - GSencript"
                mensagem_texto = (
                    f"Olá, {user.first_name or user.username}.\n\n"
                    f"Recebemos uma solicitação para redefinir a senha da sua conta no GSencript.\n"
                    f"Para criar uma nova senha, utilize o link abaixo:\n\n"
                    f"{url_redefinicao}\n\n"
                    f"Este link é válido por 10 minutos. Se não foi você quem solicitou, "
                    f"pode ignorar este e-mail com segurança; seus dados continuam criptografados."
                )
                
                # Dispara o e-mail via Brevo (puxando as credenciais do settings)
                send_mail(
                    subject=assunto,
                    message=mensagem_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                # Registra o evento no log de auditoria do sistema para fins de PSI
                AuditLog.objects.create(
                    usuario=user,
                    evento="RECUPERACAO_SOLICITADA",
                    ip_origem=request.META.get('REMOTE_ADDR'),
                    detalhes="Token de recuperação gerado e enviado para o e-mail cadastrado."
                )
                
                # Resposta segura: NUNCA retorne o token no JSON da resposta!
                return JsonResponse({
                    "mensagem": "Se o e-mail estiver cadastrado, um link de redefinição válido por 15 minutos será enviado."
                }, status=200)
                
            # Tratamento de segurança (Enumeration Attack Mitigation):
            # Para evitar que invasores descubram quais e-mails estão cadastrados,
            # você pode retornar a mesma mensagem de sucesso mesmo se o e-mail não existir.
            return JsonResponse({
                "mensagem": "Se o e-mail estiver cadastrado, um link de redefinição válido por 15 minutos será enviado."
            }, status=200)
            
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)
            
    return JsonResponse({"erro": "Método não permitido"}, status=405)


@csrf_exempt
def resetar_senha(request):
    # Caso o usuário chegue clicando no link do e-mail (GET), renderiza a tela de nova senha
    if request.method == 'GET':
        token = request.GET.get('token', '')
        return render(request, 'recovery/resetar.html', {'token': token})
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            nova_senha = data.get('nova_senha')
            
            user = get_object_or_404(User, recovery_token=token)
            
            # Verifica expiração do token
            if timezone.now() > user.token_expiration:
                return JsonResponse({"erro": "O token de recuperação expirou."}, status=400)
                
            # Define a nova senha usando o hashing robusto do Argon2 automaticamente
            user.set_password(nova_senha)
            user.recovery_token = None  # Invalida o token imediatamente após o uso
            user.token_expiration = None
            user.save()
            
            AuditLog.objects.create(
                usuario=user,
                evento="RECUPERACAO_SUCESSO",
                ip_origem=request.META.get('REMOTE_ADDR'),
                detalhes="Senha mestra alterada com sucesso via token de recuperação."
            )
            return JsonResponse({"mensagem": "Senha atualizada com sucesso!"}, status=200)
            
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=400)
            
    return JsonResponse({"erro": "Método não permitido"}, status=405)