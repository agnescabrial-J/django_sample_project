# customer/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


# ── TENANT ──────────────────────────────────────────────────────
class Tenant(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=100)
    company    = models.CharField(max_length=100, unique=True)
    email      = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company


# ── USER MANAGER ─────────────────────────────────────────────────
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


# ── USER ─────────────────────────────────────────────────────────
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_SUPERUSER = "superuser"
    ROLE_USER      = "user"
    ROLE_CHOICES   = [
        (ROLE_SUPERUSER, "Super User"),
        (ROLE_USER,      "User"),
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant     = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="users")
    email      = models.EmailField(unique=True)
    name       = models.CharField(max_length=150)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.tenant.company})"

    @property
    def is_tenant_superuser(self):
        return self.role == self.ROLE_SUPERUSER


# ── CUSTOMER ──────────────────────────────────────────────────────
class Customer(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant     = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="customers")
    name       = models.CharField(max_length=150)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_customers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "email")

    def __str__(self):
        return f"{self.name} [{self.tenant.company}]"