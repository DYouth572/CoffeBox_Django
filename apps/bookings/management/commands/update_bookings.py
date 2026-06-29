from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bookings.models import Booking

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Chuyển từ 'confirmed' sang 'active' nếu đã đến giờ
        Booking.objects.filter(status='confirmed', start_time__lte=now).update(status='active')
        # Chuyển từ 'active' sang 'completed' nếu đã quá giờ kết thúc
        Booking.objects.filter(status='active', end_time__lte=now).update(status='completed')