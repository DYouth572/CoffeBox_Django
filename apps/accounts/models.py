from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Khách hàng'),
        ('staff', 'Nhân viên'),
        ('admin', 'Quản trị viên'),
    )
    
    role = models.CharField("Vai trò", max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField("Số điện thoại", max_length=15, blank=True, null=True)
    avatar = models.ImageField("Ảnh đại diện", upload_to='avatars/', default='avatars/default.png', blank=True, null=True)

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Danh sách người dùng"

    def __str__(self):
        return self.username