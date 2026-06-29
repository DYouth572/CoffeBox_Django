from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.boxes.models import Box

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ phê duyệt'),
        ('confirmed', 'Chờ check-in'),
        ('active', 'Đang sử dụng'),
        ('completed', 'Hoàn thành'),
        ('cancellation_pending', 'Chờ duyệt hủy'),
        ('cancelled', 'Đã hủy'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    box = models.ForeignKey(Box, verbose_name="Không gian Box", on_delete=models.PROTECT, related_name='bookings')
    start_time = models.DateTimeField("Thời gian bắt đầu")
    end_time = models.DateTimeField("Thời gian kết thúc")
    total_price = models.DecimalField("Tổng tiền", max_digits=10, decimal_places=2, default=0, editable=False)
    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    checked_in_at = models.DateTimeField("Thời gian check-in", blank=True, null=True)
    cancellation_reason = models.CharField("Lý do khách yêu cầu hủy", max_length=100, blank=True)
    cancellation_note = models.TextField("Ghi chú xử lý hủy", blank=True)
    cancellation_requested_at = models.DateTimeField("Thời gian yêu cầu hủy", blank=True, null=True)
    cancellation_previous_status = models.CharField("Trạng thái trước khi chờ hủy", max_length=20, blank=True)
    cancellation_response_message = models.TextField("Tin nhắn phản hồi hủy", blank=True)
    cancelled_at = models.DateTimeField("Thời gian hủy", blank=True, null=True)

    class Meta:
        verbose_name = "Lịch đặt"
        verbose_name_plural = "Quản lý lịch đặt"
        ordering = ['-start_time']

    def clean(self):
        """Kiểm tra logic dữ liệu trước khi lưu."""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu.")
            if self.start_time < timezone.now():
                raise ValidationError("Không thể đặt lịch trong quá khứ.")

    def save(self, *args, **kwargs):
        """Tự động tính tổng tiền trước khi lưu."""
        if self.start_time and self.end_time:
            # Tính số giờ (đổi giây sang giờ)
            duration = (self.end_time - self.start_time).total_seconds() / 3600
            # Tổng tiền = số giờ * giá của Box
            self.total_price = round(duration * float(self.box.price_per_hour), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.username} - {self.box.name} ({self.status})"

    @property
    def hours_until_start(self):
        return (self.start_time - timezone.now()).total_seconds() / 3600

    @property
    def cancellation_in_policy(self):
        hours = self.hours_until_start
        return 6 <= hours <= 24

    @property
    def preparation_minutes(self):
        return int((self.start_time - self.created_at).total_seconds() / 60)

    @property
    def is_short_notice(self):
        return self.preparation_minutes < 60
    
    @property
    def remaining_seconds(self):
        """Tính số giây còn lại nếu đơn hàng đang ở trạng thái active."""
        if self.status == 'active' and self.end_time > timezone.now():
            # Trả về số giây nguyên (integer) còn lại
            return int((self.end_time - timezone.now()).total_seconds())
        return 0 # Trả về 0 nếu không phải active hoặc đã hết giờ
    

class SupportRequest(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='support_requests')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Hỗ trợ cho {self.booking.box.name} - {self.booking.customer.username}"
