from django.utils import timezone
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ConsentimentoLGPD


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def privacidade_dashboard(request):
    """
    Endpoint da API para retornar o status e detalhes do consentimento LGPD do usuário.
    """
    try:
        consentimento = request.user.consentimento
        data = {
            "aceite_termos": consentimento.aceite_termos,
            "finalidade": consentimento.finalidade,
            "data_aceite": consentimento.data_aceite.isoformat() if consentimento.data_aceite else None,
            "versao_termo": consentimento.versao_termo,
            "consentimento_ativo": consentimento.consentimento_ativo
        }
        return Response(data, status=status.HTTP_200_OK)
    except ConsentimentoLGPD.DoesNotExist:
        return Response({"erro": "Registro de consentimento não encontrado."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revogar_consentimento(request):
    """
    Revoga o consentimento LGPD do usuário logado.
    """
    try:
        consentimento = request.user.consentimento 
        
        if not consentimento.consentimento_ativo:
            return Response({"mensagem": "O consentimento já está revogado."}, status=status.HTTP_400_BAD_REQUEST)
        
        consentimento.revogar()
        
        return Response({
            "mensagem": "Consentimento revogado com sucesso. O acesso a certas funcionalidades foi suspenso."
        }, status=status.HTTP_200_OK)
        
    except ConsentimentoLGPD.DoesNotExist:
        return Response({"erro": "Registro de consentimento não encontrado."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_meus_dados(request):
    """
    Consulta os dados de perfil e consentimento do titular.
    """
    user = request.user
    
    try:
        consentimento = user.consentimento
        lgpd_info = {
            "aceite_termos": consentimento.aceite_termos,
            "finalidade": consentimento.finalidade,
            "data_aceite": consentimento.data_aceite.strftime("%d/%m/%Y %H:%M:%S") if consentimento.data_aceite else None,
            "versao_termo": consentimento.versao_termo,
            "status_consentimento": "Ativo" if consentimento.consentimento_ativo else "Revogado"
        }
    except ConsentimentoLGPD.DoesNotExist:
        lgpd_info = "Registro de consentimento não encontrado."

    dados_titular = {
        "usuario": user.username,
        "email": user.email,
        "data_cadastro": user.date_joined.strftime("%d/%m/%Y %H:%M:%S"),
        "lgpd": lgpd_info
    }

    return Response(dados_titular, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_meus_dados(request):
    """
    Exporta todos os dados do titular em formato JSON para download (Direito de Portabilidade).
    """
    user = request.user
    
    # 1. Dados de Identificação do Usuário
    perfil = {
        "username": user.username,
        "email": user.email,
        "nome": user.first_name,
        "sobrenome": user.last_name,
        "data_cadastro": user.date_joined.isoformat(),
    }
    
    # 2. Histórico de Consentimento (LGPD)
    try:
        consentimento = user.consentimento
        lgpd_info = {
            "aceite_termos": consentimento.aceite_termos,
            "finalidade": consentimento.finalidade,
            "data_aceite": consentimento.data_aceite.isoformat() if consentimento.data_aceite else None,
            "versao_termo": consentimento.versao_termo,
            "status_atual": "Ativo" if consentimento.consentimento_ativo else "Revogado"
        }
    except ConsentimentoLGPD.DoesNotExist:
        lgpd_info = "Sem registro de consentimento."

    # 3. Estrutura Final do Arquivo
    dados_exportacao = {
        "exportado_em": timezone.now().isoformat(),
        "aplicacao": "Jano Desk - Help Desk System",
        "titular": perfil,
        "conformidade_lgpd": lgpd_info
    }

    response = Response(dados_exportacao, status=status.HTTP_200_OK)
    
    # Cabeçalho para forçar o download do JSON no navegador/client
    response['Content-Disposition'] = f'attachment; filename="meus_dados_lgpd_{user.username}.json"'
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def excluir_minha_conta(request):
    """
    Executa a exclusão da conta do usuário (Direito ao Esquecimento).
    """
    user = request.user
    try:
        logout(request)
        user.delete()
        
        return Response({
            "mensagem": "Sua conta e seus dados foram apagados conforme a LGPD (Direito ao Esquecimento)."
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"erro": f"Erro ao processar exclusão: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aceitar_termos_novamente(request):
    """
    Renova ou reativa o consentimento LGPD do usuário.
    """
    try:
        consentimento = request.user.consentimento
        consentimento.consentimento_ativo = True
        consentimento.data_aceite = timezone.now()
        consentimento.save()
        
        return Response({"mensagem": "Consentimento renovado com sucesso!"}, status=status.HTTP_200_OK)
    except ConsentimentoLGPD.DoesNotExist:
        return Response({"erro": "Registro de consentimento não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"erro": f"Erro ao reativar consentimento: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)