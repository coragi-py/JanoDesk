from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class MyUserAdmin(UserAdmin):

    # Campos a serem exibidos na lista de usuários
    list_display = ('email', 'password','first_name', 'last_name', 'is_staff', 'date_joined')

    #Ordenação
    ordering = ('email',)

    # Filtros laterais para facilitar a busca
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    # Barra de busca para encontrar usuários rapidamente
    search_fields = ('email', 'first_name', 'last_name')

    # Campos somente leitura para evitar alterações acidentais
    readonly_fields = ('date_joined',)

    # Configuração dos campos dentro da edição do usuário
    # Campo de segredo 2FA apenas como leitura
    fieldsets = UserAdmin.fieldsets + (
        ('Autenticação de Dois Fatores', {
            'fields': ('two_factor_secret', 'recovery_token', 'token_expiration'),
        }),
    )

    readonly_fields = ('two_factor_secret', 'recovery_token', 'token_expiration')