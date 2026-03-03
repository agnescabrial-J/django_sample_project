# customer/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Customer
from .serializers import TenantSignupSerializer, UserCreateSerializer, CustomerSerializer
from .permissions import IsTenantSuperUser


# ── 1. TENANT SIGNUP  –  POST /api/signup/ ───────────────────────────────────
#    Public. Creates Tenant + first SuperUser. Returns JWT tokens.
# ─────────────────────────────────────────────────────────────────────────────
class TenantSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TenantSignupSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            tenant = result["tenant"]
            user   = result["user"]

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Tenant and super user created successfully.",
                    "tenant": {
                        "id":      str(tenant.id),
                        "company": tenant.company,
                    },
                    "user": {
                        "id":    str(user.id),
                        "email": user.email,
                        "role":  user.role,
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access":  str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── 2. CREATE / LIST USERS  –  /api/users/ ───────────────────────────────────
#    Only the tenant's superuser may create users.
#    Any authenticated user can list users in their tenant.
# ─────────────────────────────────────────────────────────────────────────────
class CreateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all users in the logged-in user's tenant."""
        users = User.objects.filter(tenant=request.user.tenant).values(
            "id", "name", "email", "role", "created_at"
        )
        tenant_company = request.user.tenant.company
        result = [{"tenant_company": tenant_company, **u} for u in users]
        return Response(result)

    def post(self, request):
        """Create a new user — superuser only."""
        if not request.user.is_tenant_superuser:
            return Response(
                {"error": "Only the tenant super user can create users."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User created successfully.",
                    "user": {"id": str(user.id), "email": user.email},
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── 3. CUSTOMER LIST / CREATE  –  /api/customers/ ────────────────────────────
#    Returns ONLY the logged-in user's tenant customers.
# ─────────────────────────────────────────────────────────────────────────────
class CustomerListCreateView(generics.ListCreateAPIView):
    serializer_class   = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # KEY isolation: filter strictly by tenant
        return Customer.objects.filter(
            tenant=self.request.user.tenant
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save()


# ── 4. CUSTOMER DETAIL  –  /api/customers/<pk>/ ──────────────────────────────
class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(tenant=self.request.user.tenant)