from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.conf import settings
import random
import datetime
from datetime import datetime, timedelta
from django.utils import timezone

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SELLER = 'SELLER', 'Seller'
        CLIENT = 'CLIENT', 'Client'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name='Роль'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default='avatars/default_avatar.png',
        verbose_name='Аватар'
    )
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER or self.role == self.Role.ADMIN

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    def get_absolute_url(self):
        return reverse('index')

    def __str__(self):
        return self.username

class OTPCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username} - {self.code}"