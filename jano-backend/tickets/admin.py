from django.contrib import admin
from .models import Category, SlaConfig, Ticket, TicketMessage, TicketAttachment

# Registra as tabelas de chamados no painel gerencial
admin.site.register(Category)
admin.site.register(SlaConfig)
admin.site.register(Ticket)
admin.site.register(TicketMessage)
admin.site.register(TicketAttachment)