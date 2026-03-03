# customer/serializers.py

from rest_framework import serializers
from .models import Tenant, User, Customer


# ── 1. TENANT SIGNUP ─────────────────────────────────────────────────────────
class TenantSignupSerializer(serializers.Serializer):
    tenant_name      = serializers.CharField(max_length=100)
    company          = serializers.CharField(max_length=100)
    tenant_email     = serializers.EmailField()
    superuser_name   = serializers.CharField(max_length=150)
    superuser_email  = serializers.EmailField()
    password         = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    # ── Field-level validations (run before create) ──────────────────────────
    def validate_company(self, value):
        if Tenant.objects.filter(company__iexact=value).exists():
            raise serializers.ValidationError(
                "A tenant with this company name already exists."
            )
        return value

    def validate_tenant_email(self, value):
        if Tenant.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A tenant with this email already exists."
            )
        return value

    def validate_superuser_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        # Create Tenant
        tenant = Tenant.objects.create(
            name    = validated_data["tenant_name"],
            company = validated_data["company"],
            email   = validated_data["tenant_email"],
        )
        # Create first SuperUser for this tenant
        user = User.objects.create_user(
            email    = validated_data["superuser_email"],
            password = validated_data["password"],
            name     = validated_data["superuser_name"],
            tenant   = tenant,
            role     = User.ROLE_SUPERUSER,
        )
        return {"tenant": tenant, "user": user}


# ── 2. USER CREATE (by superuser) ─────────────────────────────────────────────
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ["name", "email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        return User.objects.create_user(
            email    = validated_data["email"],
            password = validated_data["password"],
            name     = validated_data["name"],
            tenant   = request.user.tenant,
            role     = User.ROLE_USER,
        )


# ── 3. CUSTOMER (tenant-scoped CRUD) ─────────────────────────────────────────
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Customer
        fields = ["id", "name", "email", "phone", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        return Customer.objects.create(
            tenant     = request.user.tenant,
            created_by = request.user,
            **validated_data,
        )