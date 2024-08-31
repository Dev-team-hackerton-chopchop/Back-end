from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Profile
# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_id = models.CharField(max_length=128, unique=True)
    title = models.CharField(max_length=128)
    content = models.TextField()
    nickname = models.CharField(max_length=128)

    def __str__(self):
        return self.title

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.CharField(max_length=1, choices=[('O', '동의'), ('X', '비동의')])
    transaction_hash = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'voter')

    def __str__(self):
        return f"{self.voter.username}의 {self.post.title}에 대한 투표"