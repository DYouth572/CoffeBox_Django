from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.boxes.models import Box
from .models import Booking, SupportRequest

User = get_user_model()

class BookingsModelTestCase(TestCase):
    """1. KIỂM THỬ TẦNG MODEL (Logic nghiệp vụ và định dạng chuỗi)"""

    def setUp(self):
        self.user = User.objects.create_user(username="testcustomer", password="CoffeeBox@2026!")
        self.box = Box.objects.create(name="Study Box 01", price_per_hour=Decimal('50000.00'), status='available', capacity=4)

    def test_booking_calculates_total_price_correctly(self):
        """Testcase 1: Kiểm tra tính tổng tiền tự động khi lưu đơn đặt phòng"""
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=3) # Thuê 3 tiếng
        booking = Booking.objects.create(customer=self.user, box=self.box, start_time=start, end_time=end, status='pending')
        
        # Kỳ vọng: 3 giờ * 50,000đ = 150,000đ
        self.assertEqual(booking.total_price, Decimal('150000.00'))

    def test_booking_str_representation(self):
        """Testcase 2: Kiểm tra hàm chuỗi hiển thị __str__ của model đơn đặt phòng"""
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        booking = Booking.objects.create(customer=self.user, box=self.box, start_time=start, end_time=end)
        
        self.assertIn("testcustomer", str(booking))
        self.assertIn("Study Box 01", str(booking))


class BookingsViewsTestCase(TestCase):
    """2. KIỂM THỬ TẦNG VIEWS (Xử lý HTTP Requests, API JSON, Phân quyền bảo mật)"""

    def setUp(self):
        self.user_a = User.objects.create_user(username="user_alpha", password="CoffeeBox@2026!")
        self.user_b = User.objects.create_user(username="user_beta", password="CoffeeBox@2026!")
        self.box = Box.objects.create(name="Premium Box", price_per_hour=Decimal('60000.00'), status='available', capacity=4)
        
        # Mặc định đăng nhập tài khoản user_a cho các kịch bản view thông thường
        self.client.login(username="user_alpha", password="CoffeeBox@2026!")

    def test_book_box_success(self):
        """Testcase 3: Đặt lịch phòng thành công với ngày giờ ở tương lai"""
        future_time_str = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.post(reverse('book_box', args=[self.box.id]), {
            'start_time': future_time_str,
            'duration': 2
        })
        # Đặt thành công phải chuyển hướng (302) và dữ liệu phải tồn tại trong DB
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(box=self.box, customer=self.user_a).exists())

    def test_book_box_past_time_fails(self):
        """Testcase 4: Hệ thống từ chối đặt phòng nếu thời gian ở quá khứ"""
        past_time_str = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.post(reverse('book_box', args=[self.box.id]), {
            'start_time': past_time_str,
            'duration': 2
        })
        # Phải chuyển hướng chặn lại (302) và không có đơn hàng nào được tạo trong DB
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(box=self.box, customer=self.user_a).exists())

    def test_book_box_not_logged_in(self):
        """Testcase 5: Chặn người dùng chưa đăng nhập đặt lịch phòng"""
        self.client.logout() # Đăng xuất
        future_time_str = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        response = self.client.post(reverse('book_box', args=[self.box.id]), {
            'start_time': future_time_str,
            'duration': 2
        })
        self.assertEqual(response.status_code, 302)

    def test_send_support_request_success(self):
        """Testcase 6: Gửi yêu cầu hỗ trợ thành công qua API JSON"""
        start = timezone.now() + timedelta(days=1)
        booking = Booking.objects.create(customer=self.user_a, box=self.box, start_time=start, end_time=start+timedelta(hours=1))
        
        response = self.client.post(reverse('send_support_request', args=[booking.id]), {
            'message': 'Phòng cần thêm khăn lau bàn ạ.'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertTrue(SupportRequest.objects.filter(booking=booking, message='Phòng cần thêm khăn lau bàn ạ.').exists())

    def test_send_support_request_empty_message(self):
        """Testcase 7: API từ chối xử lý khi gửi tin nhắn hỗ trợ trống rỗng"""
        start = timezone.now() + timedelta(days=1)
        booking = Booking.objects.create(customer=self.user_a, box=self.box, start_time=start, end_time=start+timedelta(hours=1))
        
        response = self.client.post(reverse('send_support_request', args=[booking.id]), {
            'message': '' # Để trống nội dung
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "Vui lòng nhập nội dung")

    def test_send_support_request_unauthorized(self):
        """Testcase 8: Bảo mật - Ngăn chặn phá hoại, gửi hỗ trợ vào đơn của khách hàng khác"""
        start = timezone.now() + timedelta(days=1)
        # Đơn này được tạo bởi user_b
        booking_of_user_b = Booking.objects.create(customer=self.user_b, box=self.box, start_time=start, end_time=start+timedelta(hours=1))
        
        # Client hiện tại đang đăng nhập bằng user_a cố tình tấn công gửi request
        response = self.client.post(reverse('send_support_request', args=[booking_of_user_b.id]), {
            'message': 'Hack hệ thống hỗ trợ'
        })
        # get_object_or_404 lọc theo customer=request.user sẽ không tìm thấy và bắn ra lỗi 404
        self.assertEqual(response.status_code, 404)

    def test_request_booking_cancellation_success(self):
        """Testcase 9: Gửi yêu cầu hủy lịch phòng thành công chuyển đơn sang trạng thái chờ duyệt"""
        start = timezone.now() + timedelta(days=1)
        booking = Booking.objects.create(customer=self.user_a, box=self.box, start_time=start, end_time=start+timedelta(hours=1), status='confirmed')
        
        response = self.client.post(reverse('request_booking_cancellation', args=[booking.id]), {
            'reason': 'Thay đổi lịch trình đột xuất'
        })
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancellation_pending')
        self.assertEqual(booking.cancellation_reason, 'Thay đổi lịch trình đột xuất')

    def test_request_booking_cancellation_invalid_status(self):
        """Testcase 10: Từ chối yêu cầu hủy khi đơn phòng đã ở trạng thái kết thúc hoàn thành"""
        start = timezone.now() - timedelta(days=1)
        booking = Booking.objects.create(customer=self.user_a, box=self.box, start_time=start, end_time=start+timedelta(hours=1), status='completed')
        
        response = self.client.post(reverse('request_booking_cancellation', args=[booking.id]), {
            'reason': 'Muốn hoàn lại tiền đơn cũ'
        })
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        # Hệ thống phải giữ nguyên trạng thái 'completed', không cho phép chuyển sang trạng thái chờ hủy
        self.assertEqual(booking.status, 'completed')