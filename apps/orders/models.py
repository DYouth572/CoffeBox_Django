from django.db import models
from django.conf import settings
from apps.bookings.models import Booking


# 1. Định nghĩa Sản phẩm
class Product(models.Model):
    name = models.CharField("Tên sản phẩm", max_length=100)
    price = models.DecimalField("Giá", max_digits=10, decimal_places=0) # Dùng số nguyên cho tiền Việt
    stock = models.IntegerField("Số lượng tồn kho", default=0)
    is_active = models.BooleanField("Đang kinh doanh", default=True)
    image = models.ImageField("Hình ảnh sản phẩm", upload_to='products/', blank=True, null=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"

    def __str__(self):
        return self.name

# 2. Định nghĩa Đơn hàng (Hợp nhất từ BookingOrder/Order)
class Order(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Đã gửi'),
        ('preparing', 'Đang pha chế'),
        ('served', 'Đã phục vụ'),
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, verbose_name="Lịch đặt", on_delete=models.CASCADE, related_name='orders')
    total_price = models.IntegerField("Tổng tiền", default=0)
    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField("Thời gian gọi", auto_now_add=True)

    class Meta:
        verbose_name = "Đơn gọi món"
        verbose_name_plural = "Danh sách đơn gọi món"

    def __str__(self):
        return f"Đơn #{self.id} - {self.booking}"

# 3. Định nghĩa Chi tiết đơn hàng
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField("Tên món", max_length=255)
    price = models.IntegerField("Giá tại thời điểm mua")
    quantity = models.PositiveIntegerField("Số lượng", default=1)

    class Meta:
        verbose_name = "Chi tiết món"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


