from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Profile

# author, profile, title, content, image, likes, published_date, end_date
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    title = models.CharField(max_length=128)
    content = models.TextField()
    image = models.ImageField(upload_to='post/', blank=True)
    likes = models.ManyToManyField(User, related_name='like_posts', blank=True) # ManyToManyField
    published_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True) # 마감일, 수정 필요 --------------------
