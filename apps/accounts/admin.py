from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Hiển thị các trường trong danh sách người dùng ở trang Admin
    list_display = ('username', 'email', 'role', 'phone', 'is_staff')
    
    # Thêm các trường vào khung chỉnh sửa (cần kế thừa từ fieldsets của UserAdmin)
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin cá nhân', {
            'fields': ('role', 'phone', 'avatar'),
        }),
    )
    
    # Hiển thị các trường khi thêm mới người dùng
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin cá nhân', {
            'fields': ('role', 'phone', 'avatar'),
        }),
    )