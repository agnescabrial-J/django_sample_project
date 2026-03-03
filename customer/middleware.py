"""
TenantMiddleware
─────────────────
Attaches `request.tenant` by reading the JWT token's user and
looking up their linked tenant.  This is the correct approach
because:
  • Signup endpoint doesn't need a tenant (it CREATES one)
  • All other endpoints authenticate via JWT, so the user's tenant
    is available through request.user.tenant — no need to read
    `company` from the request body.
"""

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Defer tenant resolution until after authentication middleware
        # has run (i.e., after DRF sets request.user).
        request.tenant = None
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Called after authentication; safe to read request.user."""
        if hasattr(request, "user") and request.user.is_authenticated:
            request.tenant = getattr(request.user, "tenant", None)
        return None