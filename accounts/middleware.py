import time

from .models import RequestLog

SKIP_PREFIXES = ("/static/", "/admin/jsi18n/")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        if not request.path.startswith(SKIP_PREFIXES):
            duration_ms = int((time.monotonic() - start) * 1000)
            try:
                RequestLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    path=request.path[:255],
                    method=request.method,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    remote_addr=request.META.get("REMOTE_ADDR"),
                )
            except Exception:
                pass
        return response
