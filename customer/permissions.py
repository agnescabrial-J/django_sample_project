from rest_framework.permissions import BasePermission


class IsTenantSuperUser(BasePermission):
    """
    Grants access only if the authenticated user has role='superuser'
    within their own tenant.
    """
    message = "Only the tenant super user can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_tenant_superuser
        )