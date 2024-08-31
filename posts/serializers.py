from rest_framework import serializers

from users.serializers import ProfileSerializer
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("pk", "vote_id", "title", "content", "nickname")


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("vote_id", "title", "content", "nickname")
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        validated_data['nickname'] = user.profile.nickname
        return super().create(validated_data)