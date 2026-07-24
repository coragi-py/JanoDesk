import os
from dotenv import load_dotenv
from pathlib import Path
from django.contrib.auth.hashers import Argon2PasswordHasher
import dj_database_url

# Valores baseados nas recomendações da RFC9106 e OWASP
class CustomArgon2Hasher(Argon2PasswordHasher):
  time_cost = 2 # Numero de iterações sobre a memoria
  memory_cost = 65536 # 64mb utilizados na memoria para inviabilizar ataques por hardware
  parallelism = 1 # Numero de threads em paralelo

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/


SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'gsencript.local']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',         # Permite que o Django Admin seja utilizado para gestão de usuários e dados
    'django.contrib.auth',          # Fornece funcionalidades de autenticação e autorização
    'django.contrib.contenttypes',  # Necessário para o framework de permissões do Django
    'django.contrib.sessions',      # Gerencia sessões de usuários, permitindo que dados persistam entre requisições
    'django.contrib.messages',      # Permite que mensagens de feedback sejam enviadas aos usuários, como notificações de sucesso ou erro
    'django.contrib.staticfiles',   # Gerencia arquivos estáticos (CSS, JavaScript, imagens) para o Django Admin e DRF
    
    # --- Bibliotecas da API ---
    'rest_framework', # Django Rest Framework para construção de APIs RESTful
    'corsheaders',    # Permite que o Next.js (ou qualquer outro front-end) consuma esta API
    'axes',           # Segurança: Proteção contra ataques de força bruta

    # --- Microsserviços de Segurança e auditoria ---
    'accounts',         # Gestão de Usuários e Autenticação
    'authentication',   # Autenticação de Usuários
    'audit',            # Auditoria de Ações e Eventos
    'recovery',         # Recuperação de Senhas
    'lgpd',             # Gestão de Consentimento e Privacidade

    # --- Microsserviços de chamados ---
    'tickets',    # Gestão de Chamados e SLA
    'assets',     # CMDB / Gestão de Ativos
    'knowledge',  # Base de Conhecimento
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # Protege contra algumas vulnerabilidades de segurança comuns, como ataques de clickjacking e injeção de código
    'corsheaders.middleware.CorsMiddleware',                    # Permite que o Next.js (ou qualquer outro front-end) consuma esta API, adicionando cabeçalhos CORS apropriados às respostas
    'django.contrib.sessions.middleware.SessionMiddleware',     # Gerencia sessões de usuários, permitindo que dados persistam entre requisições
    'django.middleware.common.CommonMiddleware',                # Fornece várias funcionalidades úteis, como redirecionamento de URLs e manipulação de cabeçalhos HTTP
    'django.middleware.csrf.CsrfViewMiddleware',                # Protege contra ataques CSRF (Cross-Site Request Forgery) verificando tokens de autenticação em formulários#   
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Associa usuários autenticados às requisições, permitindo que o Django saiba quem está fazendo a requisição
    'django.contrib.messages.middleware.MessageMiddleware',     # Permite que mensagens de feedback sejam enviadas aos usuários, como notificações de sucesso ou erro
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # Protege contra ataques de clickjacking, adicionando cabeçalhos HTTP que impedem que a página seja carregada em iframes de outros domínios
    'axes.middleware.AxesMiddleware',                           # Segurança: Proteção contra ataques de força bruta, monitorando tentativas de login e bloqueando usuários após várias tentativas falhas
]

# Templates configuration, configurado para o Django Admin e DRF, mas não utilizado pelo Next.js, que é um front-end separado
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'core.urls' # Configuração do arquivo de URLs raiz do projeto, que define como as requisições HTTP são roteadas para diferentes aplicativos e visualizações dentro do projeto Django.

WSGI_APPLICATION = 'core.wsgi.application' # Configuração do arquivo WSGI (Web Server Gateway Interface) do projeto, que serve como ponto de entrada para servidores web compatíveis com WSGI, permitindo que eles se comuniquem com a aplicação Django.


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600, # Persistência de conexões para melhorar performance. O valor de 600 segundos (10 minutos) é uma prática recomendada para reduzir a sobrecarga de criação de novas conexões, especialmente em ambientes de produção com alto tráfego.
        conn_health_checks=True, # Verificação de saúde das conexões para evitar conexões inválidas. Definido como True, o Django realizará verificações de saúde nas conexões do banco de dados antes de reutilizá-las, garantindo que apenas conexões válidas sejam utilizadas e evitando erros inesperados durante a execução da aplicação.
    )
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'accounts.User' # Modelo de usuário personalizado para a aplicação

# Configurações de validação de senha para garantir que os usuários escolham senhas fortes e seguras, protegendo contra ataques de força bruta e adivinhação de senhas.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', # Validador que verifica se a senha do usuário é semelhante a atributos do usuário, como nome de usuário ou e-mail, para evitar senhas fracas e previsíveis.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', # Validador que garante que a senha do usuário tenha um comprimento mínimo, aumentando a segurança ao exigir senhas mais longas e complexas.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', # Validador que verifica se a senha do usuário é uma das senhas comuns e fáceis de adivinhar.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configurações de autenticação para a aplicação, incluindo backends de autenticação e algoritmos de hash de senha.
AUTHENTICATION_BACKENDS = [
  'axes.backends.AxesBackend', # Adiciona proteção contra ataques de força bruta, monitorando tentativas de login e bloqueando usuários após várias tentativas falhas.
  'django.contrib.auth.backends.ModelBackend', # Permite autenticação baseada em modelo de usuário, utilizando o modelo de usuário personalizado definido na aplicação.
]

# Configurações de hash de senha para a aplicação, utilizando algoritmos seguros e resistentes a ataques de força bruta e ataques de hardware.
PASSWORD_HASHERS = [
    'core.settings.CustomArgon2Hasher', # Utiliza o algoritmo Argon2 para hash de senhas, que é considerado um dos algoritmos mais seguros e resistentes a ataques de força bruta e ataques de hardware.
    'django.contrib.auth.hashers.PBKDF2PasswordHasher', # Utiliza o algoritmo PBKDF2 para hash de senhas, que é um algoritmo amplamente utilizado e recomendado para proteger senhas armazenadas em bancos de dados.
]

# Configurações de sessão para a aplicação, incluindo tempo de expiração e comportamento ao fechar o navegador.
SESSION_COOKIE_AGE = 1800  # 30 minutos em segundos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Assegura que a sessão do usuário seja encerrada quando o navegador for fechado, aumentando a segurança ao evitar que sessões permaneçam ativas em dispositivos compartilhados ou públicos.

# Configuração do bloqueio (Axes)
AXES_FAILURE_LIMIT = 5 # Número máximo de tentativas de login falhas antes de bloquear o usuário
AXES_COOLOFF_TIME = 0.25 # 15 minutos (em horas). Após esse período, o usuário poderá tentar fazer login novamente.
AXES_LOCK_OUT_AT_FAILURE_LIMIT = True # Bloqueia o usuário após atingir o limite de tentativas falhas

# Configurações de segurança de transporte
SECURE_SSL_REDIRECT = False                                   # Em produção, deve ser True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # Cabeçalho que indica se a requisição foi feita via HTTPS
SESSION_COOKIE_SECURE = False                                 # Em produção, deve ser True
CSRF_COOKIE_SECURE = False                                    # Em produção, deve ser True
SECURE_HSTS_SECONDS = 31536000                                # 1 ano em segundos. O valor é definido para 1 ano (em segundos) para garantir que os navegadores mantenham essa política por um período prolongado.
SECURE_HSTS_INCLUDE_SUBDOMAINS = True                         # Incluir subdomínios na política HSTS para garantir que todas as partes do site sejam protegidas
SECURE_HSTS_PRELOAD = True                                    # Incluir o site na lista de pré-carregamento HSTS dos navegadores para garantir que os navegadores apliquem a política HSTS mesmo antes da primeira visita ao site

# Configurações de E-mail via SMTP (Brevo)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'       # Define o backend de e-mail como SMTP, permitindo que o Django envie e-mails através de um servidor SMTP.
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp-relay.brevo.com')   # Define o host do servidor SMTP, utilizando a variável de ambiente EMAIL_HOST ou, se não estiver definida, o valor padrão 'smtp-relay.brevo.com'.
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))                 # Define a porta do servidor SMTP, utilizando a variável de ambiente EMAIL_PORT ou, se não estiver definida, o valor padrão 587 (porta padrão para envio de e-mails com STARTTLS).
EMAIL_USE_TLS = True                                                # Requisito de segurança do Brevo para conexões SMTP
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')                 # Define o usuário do servidor SMTP, utilizando a variável de ambiente EMAIL_HOST_USER. Este valor é necessário para autenticação no servidor SMTP.
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')         # Define a senha do servidor SMTP, utilizando a variável de ambiente EMAIL_HOST_PASSWORD. Este valor é necessário para autenticação no servidor SMTP.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')           # Define o endereço de e-mail padrão para envio de e-mails, utilizando a variável de ambiente DEFAULT_FROM_EMAIL. Este valor será utilizado como remetente nos e-mails enviados pela aplicação.


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True # Habilita a internacionalização, permitindo que a aplicação suporte múltiplos idiomas e formatos de data/hora.

USE_TZ = True # Habilita o uso de fusos horários, permitindo que a aplicação lide corretamente com datas e horários em diferentes regiões do mundo.

# ==========================================
# CONFIGURAÇÕES DA API HEADLESS (DRF + CORS)
# ==========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # Permite que a API utilize sessões de usuário para autenticação, permitindo que usuários autenticados possam acessar recursos protegidos da API.
        'rest_framework.authentication.BasicAuthentication',    # Permite que a API utilize autenticação básica HTTP, permitindo que usuários forneçam um nome de usuário e senha para acessar recursos protegidos da API.
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',           # Define a permissão padrão para a API como "IsAuthenticated", garantindo que apenas usuários autenticados possam acessar os recursos da API.
    ),
}

# Configurações de CORS (Cross-Origin Resource Sharing) para permitir que o front-end consuma a API Django, definindo quais origens são permitidas e se credenciais podem ser incluídas nas requisições.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # Permite que o front-end em desenvolvimento acesse a API Django durante o desenvolvimento local.
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True # Permite que credenciais (como cookies e cabeçalhos de autenticação) sejam incluídas nas requisições CORS, garantindo que usuários autenticados possam acessar recursos protegidos da API a partir do front-end.

# Static files (CSS, JavaScript, Images) apenas para o Django Admin e DRF
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# ==========================================
# CONFIGURAÇÃO DE PSEUDONIMIZAÇÃO (LGPD)
# ==========================================
# Por padrão, usa a SECRET_KEY. 
# Definir um SALT fixo garante maior consistência na derivação da chave do Fernet/AES.
CRYPTOGRAPHY_SALT = os.getenv('CRYPTOGRAPHY_SALT', SECRET_KEY[:16])