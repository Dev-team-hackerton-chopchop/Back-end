from django.contrib.auth.models import User # User model
from django.contrib.auth.password_validation import validate_password # Django password validation

from rest_framework import serializers
from rest_framework.authtoken.models import Token # Token model
from rest_framework.validators import UniqueValidator # 이메일 중복 방지를 위한 검증 도구

from django.contrib.auth import authenticate

from .models import Profile

class RegisterSerializer(serializers.ModelSerializer): # 회원가입 Serializer
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())] # 중복 방지
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # 비밀번호 검증
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password': '비밀번호가 일치하지 않습니다.'})
        return data
        
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user
    

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
        fields = ("nickname", "department", "image")