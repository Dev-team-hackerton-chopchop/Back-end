from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Profile
# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_id = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    content = models.TextField()
    nickname = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.author.profile.nickname
        super().save(*args, **kwargs)
