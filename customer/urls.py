from django.urls import path
from customer.views import CustomerSignupView

urlpatterns=[
    path("Signup/", CustomerSignupView.as_view())
]