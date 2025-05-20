from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.conf import settings
import random
import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files.storage import default_storage
import os

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

    # Define a default avatar constant path that exists in your media directory
    DEFAULT_AVATAR_PATH = 'avatars/default_avatar.png'

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default=DEFAULT_AVATAR_PATH,
        verbose_name='Аватар'
    )
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    
    def set_default_avatar(self):
        """Set the avatar to the default image"""
        if self.avatar and self.avatar.name != self.DEFAULT_AVATAR_PATH:
            # Store the old avatar path to delete it after changing
            old_avatar = self.avatar.path if hasattr(self.avatar, 'path') else None
            
            # Set to default avatar
            self.avatar = self.DEFAULT_AVATAR_PATH
            self.save(update_fields=['avatar'])
            
            # Delete the old avatar file if it exists and isn't the default
            if old_avatar and os.path.exists(old_avatar):
                try:
                    os.remove(old_avatar)
                except (OSError, FileNotFoundError):
                    # Log error if needed but don't break the flow
                    pass
        
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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp_code')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username} - {self.code}"

class SellerApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Күтуде'),
        ('approved', 'Бекітілген'),
        ('rejected', 'Қабылданбаған'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='seller_applications')
    reason = models.TextField(verbose_name='Сатушы болу себебі')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Мәртебесі')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Қаралған уақыты')
    admin_comment = models.TextField(blank=True, null=True, verbose_name='Әкімші түсініктемесі')
    
    class Meta:
        verbose_name = 'Сатушы болу өтініші'
        verbose_name_plural = 'Сатушы болу өтініштері'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"
    
    def approve(self, admin_comment=None):
        from django.utils import timezone
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        if admin_comment:
            self.admin_comment = admin_comment
        self.save()
        
        self.user.role = CustomUser.Role.SELLER
        self.user.save()
        
        return True
    
    def reject(self, admin_comment=None):
        from django.utils import timezone
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        if admin_comment:
            self.admin_comment = admin_comment
        self.save()
        return True