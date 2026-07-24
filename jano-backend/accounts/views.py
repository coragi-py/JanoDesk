import json
import pyotp
import re
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import User
from lgpd.models import ConsentimentoLGPD
from django.shortcuts import render

def validar_senha_forte(senha):
    # Regra de complexidade da senha
    if len(senha) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."
    if not re.search(r"[A-Z]", senha) or not re.search(r"[a-z]", senha):
        return False, "A senha deve conter letras maiúsculas e minúsculas."
    if not re.search(r"[0-9]", senha) or not re.search(r"[!@#$%^&*()]", senha):
        return False, "A senha deve conter números e caracteres especiais."
    return True, ""

@csrf_exempt
def registrar_usuario(request):
    if request.method == 'GET':
        return render(request, 'accounts/registrar.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('full_name', '')
            email = data.get('email', '').strip().lower()
            username = data.get('username').strip().lower()
            senha = data.get('senha')
            consentimento_recebido = data.get('consentimento_lgpd')

            # Lógica para separar Nome de Sobrenome
            if full_name:
                partes_nome = full_name.split(' ', 1)
                first_name = partes_nome[0]
                last_name = partes_nome[1] if len(partes_nome) > 1 else ""
            else:
                first_name, last_name = "", ""

            #   Validação de LGPD
            if not consentimento_recebido:
                return JsonResponse({"erro": "O consentimento da LGPD é obrigatório."}, status=400)

            # Validação de Senha Forte
            valida, msg = validar_senha_forte(senha)
            if not valida:
                return JsonResponse({"erro": msg}, status=400)

            # Validação de e-mail já cadastrado
            if User.objects.filter(email=email).exists():
                return JsonResponse({"erro": "Este e-mail já está cadastrado."}, status=400)

            # Criação do Usuário
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=senha,
                    first_name=first_name,
                    last_name=last_name
                )
                user.two_factor_secret = pyotp.random_base32()
                user.save()

                # Criando o registro no app LGPD
                ConsentimentoLGPD.objects.create(
                    usuario=user,
                    aceite_termos=True,
                    versao_termo="1.0"
                )

            return JsonResponse({
                "mensagem": "Usuário criado com sucesso!",
                "2fa_secret": user.two_factor_secret
            }, status=201)
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)
        
    return JsonResponse({"erro": "Método não permitido"}, status=405)