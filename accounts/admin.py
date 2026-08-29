from django.contrib import admin

from .models import AuditEvent, RequestLog, UserProfile


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ["path", "method", "status_code", "duration_ms", "user", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(UserProfile)
admin.site.register(AuditEvent)
