from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'usuario', 'evento', 'ip_origem')
    list_filter = ('evento', 'timestamp')
    readonly_fields = ('timestamp', 'usuario', 'evento', 'ip_origem', 'detalhes')