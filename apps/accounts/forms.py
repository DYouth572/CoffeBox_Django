from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Lấy model User hiện tại (đã được định nghĩa trong AUTH_USER_MODEL ở settings.py)
User = get_user_model()

# 1. Form Đăng ký tùy chỉnh
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = None # Xóa hướng dẫn mặc định

# 2. Form chỉnh sửa thông tin tài khoản và ảnh đại diện
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'avatar', 'phone']