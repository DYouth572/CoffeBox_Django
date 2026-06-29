from django.contrib import admin
from .models import Booking

@admin.action(description='Phê duyệt đơn hàng đã chọn')
def approve_bookings(modeladmin, request, queryset):
    queryset.update(status='confirmed')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer', 'box', 'status', 'start_time', 'end_time', 'total_price']
    list_filter = ['status', 'start_time'] # Thêm bộ lọc cho tiện
    actions = [approve_bookings]
    search_fields = ('customer__username', 'box__name')


from .models import SupportRequest 

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    # Tùy chọn hiển thị các cột trong trang danh sách
    list_display = ('booking', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('booking__box__name', 'message')