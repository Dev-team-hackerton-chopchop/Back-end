from rest_framework import serializers
from users.serializers import ProfileSerializer
from .models import Post, Vote

class PostSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.profile.nickname', read_only=True)

    class Meta:
        model = Post
        fields = ("pk", "vote_id", "title", "content", "author_nickname")

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "content")
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        
        # 새로운 Post 객체를 생성합니다.
        post = Post.objects.create(**validated_data)
        
        # vote_id를 글의 번호(pk)로 설정합니다.
        post.vote_id = f"VOTE_{post.pk}"
        post.save()
        
        return post

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('id', 'post', 'voter', 'choice', 'transaction_hash')
        read_only_fields = ('voter', 'transaction_hash')