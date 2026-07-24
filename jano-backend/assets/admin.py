from django.contrib import admin
from .models import Asset

# Registra a tabela do CMDB
admin.site.register(Asset)