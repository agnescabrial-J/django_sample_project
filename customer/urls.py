from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    TenantSignupView,
    CreateUserView,
    CustomerListCreateView,
    CustomerDetailView,
)

urlpatterns = [
    # ── Auth ─────────────────────────────────────────────────────
    # path("",               index,                        name="index"), 
    path("signup/",        TenantSignupView.as_view(),    name="tenant-signup"),
    path("login/",         TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(),    name="token-refresh"),

    # ── User management (superuser only) ─────────────────────────
    path("users/",         CreateUserView.as_view(),      name="user-list-create"),

    # ── Customer data (tenant-scoped) ────────────────────────────
    path("customers/",          CustomerListCreateView.as_view(), name="customer-list"),
    path("customers/<uuid:pk>/", CustomerDetailView.as_view(),    name="customer-detail"),
]