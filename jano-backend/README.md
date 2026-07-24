# 🚀 Jano Desk - Backend Setup Guide

Bem-vindos ao repositório do **Jano Desk**! Este documento servirá como guia definitivo para configurar o ambiente de desenvolvimento local do nosso backend.

O nosso sistema utiliza uma Arquitetura Headless (API-Driven). O nosso backend foi construído utilizando Python com Django & Django REST Framework (DRF), conectando-se a um Banco de Dados PostgreSQL relacional hospedado via Docker.

---

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas na sua máquina (preferencialmente Windows 11 / WSL):

- **Python 3.12+** (Marque a opção "Add Python to PATH" durante a instalação).
- **Docker Desktop** (Para rodar o banco de dados sem poluir o SO).
- **Git** (Para controle de versão).
- **VS Code** (IDE recomendada).

---

## ⚙️ Passo a Passo de Instalação (Windows PowerShell)

### Passo 1: Clonar o Repositório e Navegar para o Backend

Abra o seu PowerShell e clone o monorepo do projeto:

```powershell
git clone https://github.com/coragi-py/janodesk.git
cd janodesk/jano-backend

```

### Passo 2: Configurar o Ambiente Virtual (venv)

O ambiente virtual isola as dependências do nosso projeto para que não haja conflito com o seu sistema operacional.

```powershell
# 1. Cria o ambiente virtual
python -m venv venv

# 2. Ativa o ambiente virtual (O prefixo '(venv)' deve aparecer no terminal)
.\venv\Scripts\Activate.ps1

# 3. Instala todas as bibliotecas necessárias da nossa API
pip install -r requirements.txt

```

_(Nota: Se der erro de permissão ao ativar o venv, abra o PowerShell como Administrador e rode: `Set-ExecutionPolicy Unrestricted -Force`, depois tente ativar novamente)._

### Passo 3: Levantar o Banco de Dados (PostgreSQL via Docker)

Com o Docker Desktop aberto em segundo plano, rode o comando abaixo para subir o nosso container isolado na porta 5432:

```powershell
docker run --name jano-postgres -e POSTGRES_DB=janodesk_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16-alpine

```

### Passo 4: Configurar as Variáveis de Ambiente (.env)

Nunca subimos senhas para o GitHub. Na raiz da pasta `jano-backend` (mesmo nível do `manage.py`), crie um arquivo chamado `.env` e adicione o seguinte conteúdo base:

```env
# Configurações Base
DEBUG=True
SECRET_KEY=sua-chave-secreta-super-segura-e-persistente-jano-desk-2026

# Conexão com o Banco de Dados (Docker)
DATABASE_URL=postgres://postgres:postgres@localhost:5432/janodesk_db

# (Futuro) Configurações SMTP para e-mails
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

```

### Passo 5: Estruturar o Banco de Dados (Migrações)

Agora precisamos que o Django crie todas as tabelas (Tickets, Assets, Users) dentro do PostgreSQL vazio que acabamos de subir.

```powershell
# 1. Aplica a estrutura no banco de dados
python manage.py migrate

# 2. Cria o seu usuário master local (Siga as instruções na tela)
python manage.py createsuperuser

```

### Passo 6: Ligar o Servidor API 🚀

Com o banco rodando e o ambiente ativado, inicie o motor principal:

```powershell
python manage.py runserver

```

- **Painel Administrativo:** Acesse `http://localhost:8000/admin` e faça login com o superuser criado no Passo 5.
- **API RESTful (JSON):** Acesse `http://localhost:8000/api/v1/tickets/chamados/` para ver a interface gráfica do DRF.

---

## 🌿 Regras de Fluxo de Trabalho (GitFlow)

Para garantirmos a integridade do código para o TCC, nunca faça commits diretos na branch `main`.

Quando for desenvolver a sua "Big Feature", crie uma branch nova:

```powershell
# Atualize seu repositório local
git pull origin main

# Crie e mude para a sua branch de trabalho (ex: feature/cmdb)
git checkout -b feature/nome-da-sua-feature

```

Ao finalizar, faça o commit utilizando o padrão Conventional Commits (ex: `feat: cria endpoints do CMDB`) e abra um Pull Request!
