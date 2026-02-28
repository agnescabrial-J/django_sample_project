from .models import Tenant
import json

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        if request.body:
            try:
                data = json.loads(request.body)
                company = data.get("company")
                if company:
                    request.tenant = Tenant.objects.get( company=company )
            except:
                request.tenant = None
        response = self.get_response(request)
        return response