from rest_framework import serializers
from .models import Customer

class CustomerSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email']
    def create(self, validated_data):
        tenant = self.context['request'].tenant
        customer = Customer.objects.create( tenant=tenant, **validated_data )
        return customer