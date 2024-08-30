from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from xrpl.core import addresscodec

import logging

logger = logging.getLogger(__name__)

from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from .models import Profile

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profile = Profile.objects.get(user=user)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'user': serializer.data,
            'xrpl_wallet_address': profile.xrpl_wallet_address
        }, status=status.HTTP_201_CREATED, headers=headers)

    def is_valid_xrpl_address(self, address):
        try:
            addresscodec.is_valid_classic_address(address)
            return True
        except ValueError:
            return False

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data
        return Response({"token": token.key}, status=status.HTTP_200_OK)
    
class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer