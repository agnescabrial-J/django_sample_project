from django.db import models
import uuid

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.company

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey( Tenant, on_delete=models.CASCADE, related_name="customers" )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name