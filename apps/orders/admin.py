from django.contrib import admin
from .models import Product, Order, OrderItem

# 1. Đăng ký Sản phẩm (Đảm bảo model Product đã được import đúng từ nơi bạn quản lý)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'is_active']
    list_editable = ['price', 'stock', 'is_active'] # Cho phép sửa nhanh trong danh sách

# 2. Inline để xem/sửa chi tiết món ngay trong đơn hàng
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Không hiển thị sẵn các dòng trống thừa

# 3. Đăng ký Đơn hàng
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Cột nào nằm trong list_display_links sẽ có đường dẫn để bấm vào xem chi tiết
    list_display = ['id', 'booking', 'status', 'total_price', 'created_at']
    list_display_links = ['id', 'booking']  # Thêm dòng này để cả ID và Lịch đặt đều bấm được
    
    list_filter = ['status', 'created_at']
    search_fields = ['booking__id']
    inlines = [OrderItemInline]