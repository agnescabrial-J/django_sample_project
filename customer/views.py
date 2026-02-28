from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSignupSerializer


class CustomerSignupView(APIView):
    def post(self, request):
        print(request, "request")
        if not request.tenant:
            return Response( {"error": "Invalid Tenant"}, status=status.HTTP_400_BAD_REQUEST )
        serializer = CustomerSignupSerializer( data=request.data, context={'request': request} )
        if serializer.is_valid():
            serializer.save()
            return Response( {"message": "Customer created successfully"},  status=status.HTTP_201_CREATED )
        return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST)