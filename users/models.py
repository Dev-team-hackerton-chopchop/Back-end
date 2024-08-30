from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# OneToOne 회원 모델
# username, email, password, nickname, department(소속), image(프로필 이미지)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=128, blank=True)
    department = models.CharField(max_length=128, blank=True)
    image = models.ImageField(upload_to='profile/', default='default.png')
    xrpl_wallet_address = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()