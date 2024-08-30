from django.contrib.auth.models import User # User model
from django.contrib.auth.password_validation import validate_password # Django password validation

from rest_framework import serializers
from rest_framework.authtoken.models import Token # Token model
from rest_framework.validators import UniqueValidator # 이메일 중복 방지를 위한 검증 도구

from django.contrib.auth import authenticate

from .models import Profile

from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    xrpl_wallet_address = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'xrpl_wallet_address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        if Profile.objects.filter(xrpl_wallet_address=attrs['xrpl_wallet_address']).exists():
            raise serializers.ValidationError({"xrpl_wallet_address": "이미 사용 중인 지갑 주소입니다."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        xrpl_wallet_address = validated_data.pop('xrpl_wallet_address')
        validated_data.pop('password2', None)
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, xrpl_wallet_address=xrpl_wallet_address)
        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        profile = Profile.objects.get(user=instance)
        ret['xrpl_wallet_address'] = profile.xrpl_wallet_address
        return ret

class LoginSerializer(serializers.Serializer): # 로그인 Serializer
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {"error": "아이디 또는 비밀번호가 일치하지 않습니다."})


class ProfileSerializer(serializers.ModelSerializer): # 프로필 Serializer
    class Meta:
        model = Profile
        fields = ("nickname", "department", "image", "xrpl_wallet_address")