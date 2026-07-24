import json
import pyotp
import traceback
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import verificar_cooldown_reenvio, gerar_e_enviar_token_email
from .models import EmailToken2FA

User = get_user_model()

@csrf_exempt
def validar_credenciais(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            return JsonResponse({"status": "ok"}, status=200)
        else:
            return JsonResponse({"erro": "E-mail ou senha incorretos."}, status=401)
    return JsonResponse({"erro": "Método inválido"}, status=405)

@csrf_exempt
def reenviar_codigo_2fa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip().lower() # Normaliza o e-mail para evitar problemas de caixa alta/baixa
            
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({"erro": "Usuário não encontrado."}, status=400)
                
            # Aplica a regra de negócio dos 30 segundos
            pode_enviar, segundos_restantes = verificar_cooldown_reenvio(user)
            
            if not pode_enviar:
                return JsonResponse({
                    "erro": f"Aguarde mais {segundos_restantes} segundos antes de solicitar um novo código."
                }, status=429) # HTTP 429: Too Many Requests
                
            # Se passou na validação, gera e envia o novo token via Brevo
            gerar_e_enviar_token_email(user)
            return JsonResponse({"mensagem": "Um novo código foi enviado para o seu e-mail."}, status=200)
            
        except Exception as e:
            print("\n" + "="*50)
            traceback.print_exc()
            print("="*50 + "\n")
            
            return JsonResponse({"erro": f"Erro interno: {str(e)}"}, status=500)

@csrf_exempt
def login_usuario(request):
    if request.method == 'GET':
        return render(request, 'authentication/login.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip().lower() # Normaliza o e-mail para evitar problemas de caixa alta/baixa
            password = data.get('password')
            token_2fa = data.get('token_2fa')
            tipo_2fa = data.get('tipo_2fa', 'app')  # "app" ou "email"

            # 1. Busca e validação inicial do usuário na base de dados
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({"erro": "Credenciais inválidas."}, status=401)

            # ---------------------------------------------------------------
            # FLUXO DE VALIDAÇÃO VIA E-MAIL (2FA ALTERNATIVO)
            # ---------------------------------------------------------------
            if tipo_2fa == 'email':
                # Captura o último token gerado que ainda não foi queimado
                ultimo_token = EmailToken2FA.objects.filter(user=user, utilizado=False).last()
                
                if not ultimo_token:
                    return JsonResponse({"erro": "Nenhum código ativo encontrado. Solicite um reenvio."}, status=400)
                
                # Executa o método do Model com validações de expiração (15min) e brute force (5 tentativas)
                valido, msg_erro = ultimo_token.validar_token(token_2fa)
                if not valido:
                    return JsonResponse({"erro": msg_erro}, status=401)
                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Especifica o backend para evitar problemas de autenticação
                return JsonResponse({
                    "mensagem": "Login realizado com sucesso!",
                    "usuario": username,
                    "redirect": "/vault/"
                }, status=200)

            # ---------------------------------------------------------------
            # FLUXO DE VALIDAÇÃO VIA APP (QR CODE / TOTP PADRÃO)
            # ---------------------------------------------------------------
            else:
                # Efetua a autenticação primária (Verificação Argon2 da senha)
                user_autenticado = authenticate(request, username=username, password=password)
                
                if user_autenticado is not None:
                    if not user_autenticado.two_factor_secret:
                        return JsonResponse({"erro": "2FA não configurado para este usuário."}, status=400)
                    
                    totp = pyotp.TOTP(user_autenticado.two_factor_secret)
                    if totp.verify(token_2fa):
                        # Inicia a sessão segura item 1.9
                        login(request, user_autenticado)
                        
                        return JsonResponse({
                            "mensagem": "Login realizado com sucesso!",
                            "usuario": username,
                            "redirect": "/vault/"
                        }, status=200)
                    else:
                        return JsonResponse({"erro": "Código 2FA inválido."}, status=401)
                else:
                    return JsonResponse({"erro": "Credenciais inválidas."}, status=401)

        except Exception as e:
            print("\n" + "="*50)
            traceback.print_exc()
            print("="*50 + "\n")
            return JsonResponse({"erro": f"Erro interno no login: {str(e)}"}, status=500)

    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def logout_usuario(request):
    if request.method == 'POST':
        # Item 1.10 Logout da sessão atual
        logout(request) 
        messages.success(request, "Você encerrou sua sessão com segurança.")
        return redirect('landing')
    
    return JsonResponse({"erro": "Método não permitido"}, status=405)