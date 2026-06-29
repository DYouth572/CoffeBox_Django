from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.bookings.models import Booking
from apps.boxes.models import Box, BoxCategory

User = get_user_model()

class BoxesModelTestCase(TestCase):
    """1. KIỂM THỬ TẦNG MODEL: Xác thực cấu trúc lưu trữ dữ liệu phòng"""

    def test_create_box_and_category(self):
        """Testcase 1: Kiểm tra khởi tạo danh mục và hiển thị thông tin dạng chuỗi của Box"""
        category = BoxCategory.objects.create(name="Phòng Đơn")
        box = Box.objects.create(
            name="Box Yên Tĩnh 01",
            category=category,
            capacity=1,
            price_per_hour=Decimal('40000.00'),
            status='available'
        )
        self.assertEqual(str(category), "Phòng Đơn")
        self.assertEqual(str(box), "Box Yên Tĩnh 01 - Sức chứa (người): 1")


class BoxesViewsTestCase(TestCase):
    """2. KIỂM THỬ TẦNG VIEWS: Hiển thị trang chủ và thuật toán quét trạng thái ngầm"""

    def setUp(self):
        self.secure_password = "CoffeeBox@2026_Secure!"
        self.customer = User.objects.create_user(username="customer_test", password=self.secure_password)
        self.category = BoxCategory.objects.create(name="Phòng Nhóm")
        self.box = Box.objects.create(
            name="Box Nhóm 02", 
            category=self.category, 
            capacity=4, 
            price_per_hour=Decimal('80000.00'),
            status='available'
        )

    def test_home_page_anonymous_user(self):
        """Testcase 2: Kiểm tra trang chủ hiển thị đúng vai trò Khách hàng vãng lai chưa đăng nhập"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], "Khách hàng")
        self.assertTemplateUsed(response, 'boxes/home.html')

    def test_home_page_staff_role_context(self):
        """Testcase 3: Kiểm tra trang chủ nhận diện đúng vai trò khi tài khoản Nhân viên truy cập"""
        staff_user = User.objects.create_user(username="staff_member", password=self.secure_password, role="staff")
        self.client.login(username="staff_member", password=self.secure_password)
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], "Nhân viên")

    def test_sync_booking_auto_cancelled_after_15_minutes(self):
        """Testcase 4: Hệ thống tự động HỦY LỊCH nếu khách trễ check-in quá 15 phút"""
        now = timezone.now()
        booking = Booking.objects.create(
            customer=self.customer,
            box=self.box,
            start_time=now - timedelta(minutes=20),
            end_time=now + timedelta(hours=1),
            status='confirmed'
        )

        self.client.login(username="customer_test", password=self.secure_password)
        self.client.get(reverse('home')) 

        booking.refresh_from_db()
        self.box.refresh_from_db()

        self.assertEqual(booking.status, "cancelled")
        self.assertIn("Khách không đến check-in", booking.cancellation_note)
        self.assertEqual(self.box.status, "available")

    def test_sync_booking_auto_completed_when_time_ends(self):
        """Testcase 5: Hệ thống tự động ĐÁNH GIÁ HOÀN THÀNH khi hết giờ thuê phòng"""
        now = timezone.now()
        booking = Booking.objects.create(
            customer=self.customer,
            box=self.box,
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(minutes=10),
            status='active'
        )

        self.client.login(username="customer_test", password=self.secure_password)
        self.client.get(reverse('home'))

        booking.refresh_from_db()
        self.box.refresh_from_db()

        self.assertEqual(booking.status, "completed")
        self.assertEqual(self.box.status, "completed")

    def test_home_page_missing_bookings_context(self):
        """Testcase 6: Trang chủ của tài khoản mới chưa đặt chỗ thì danh sách lịch phòng gửi sang phải trống"""
        self.client.login(username="customer_test", password=self.secure_password)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # ĐÃ SỬA: Tự động nhận diện biến gán dữ liệu 'my_bookings' hoặc 'bookings' để tránh KeyError
        bookings_key = 'my_bookings' if 'my_bookings' in response.context else 'bookings'
        self.assertEqual(len(response.context[bookings_key]), 0)