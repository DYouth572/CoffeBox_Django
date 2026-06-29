import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.boxes.models import Box
from apps.bookings.models import Booking
from .models import Product, Order, OrderItem

User = get_user_model()

class OrdersTestCase(TestCase):
    """BỘ 10 TESTCASES TOÀN DIỆN CHO HỆ THỐNG GỌI MÓN (ORDERS)"""

    def setUp(self):
        # Thiết lập mật khẩu mạnh đồng bộ toàn hệ thống để tránh bộ lọc bảo mật mặc định của Django
        self.secure_password = "CoffeeBox@2026_Secure!"
        self.customer = User.objects.create_user(username="coffee_lover", password=self.secure_password)
        
        # Đăng nhập tài khoản trước khi thực hiện các kịch bản view
        self.client.login(username="coffee_lover", password=self.secure_password)
        
        # Khởi tạo dữ liệu Box phụ trợ
        self.box = Box.objects.create(name="Normal Box", price_per_hour=Decimal('30000.00'), status='available', capacity=2)

        # Khởi tạo một lịch đặt đơn gốc hợp lệ thuộc về tài khoản đang test
        start = timezone.now() + timedelta(days=1)
        self.booking = Booking.objects.create(
            customer=self.customer, 
            box=self.box, 
            start_time=start, 
            end_time=start+timedelta(hours=2), 
            status='confirmed'
        )

    def test_product_str_representation(self):
        """Testcase 1: Kiểm tra định dạng hiển thị chuỗi tên sản phẩm mẫu (Model)"""
        product = Product.objects.create(name="Espresso Đá", price=30000, stock=10)
        self.assertEqual(str(product), "Espresso Đá")

    def test_order_str_representation(self):
        """Testcase 2: Kiểm tra định dạng hiển thị chuỗi của thực thể Đơn gọi món (Model)"""
        order = Order.objects.create(customer=self.customer, booking=self.booking, total_price=50000, status='submitted')
        self.assertIn(f"Đơn #{order.id}", str(order))

    def test_order_item_str_representation(self):
        """Testcase 3: Kiểm tra chuỗi định dạng dòng chi tiết sản phẩm gọi kèm (Model)"""
        order = Order.objects.create(customer=self.customer, booking=self.booking, total_price=40000, status='submitted')
        item = OrderItem.objects.create(order=order, product_name="Trà Đào", price=40000, quantity=2)
        self.assertEqual(str(item), "Trà Đào x 2")

    def test_add_order_success(self):
        """Testcase 4: Gọi món thành công với cấu trúc JSON payload hợp lệ (View)"""
        payload = {
            "booking_id": self.booking.id,
            "items": [
                {"name": "Bạc Xỉu", "price": 29000, "qty": 2},
                {"name": "Croissant", "price": 35000, "qty": 1}
            ]
        }
        response = self.client.post(reverse('add_order'), data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["total_price"], 93000)
        self.assertTrue(Order.objects.filter(booking=self.booking, total_price=93000).exists())

    def test_add_order_empty_cart(self):
        """Testcase 5: Hệ thống chặn tạo đơn khi danh sách giỏ hàng trống rỗng (View)"""
        payload = {"booking_id": self.booking.id, "items": []}
        response = self.client.post(reverse('add_order'), data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "Giỏ hàng đang trống")

    def test_add_order_no_valid_items(self):
        """Testcase 6: Hệ thống chặn và xóa đơn khi toàn bộ danh sách món gửi lên đều lỗi số lượng hoặc tên (View)"""
        payload = {
            "booking_id": self.booking.id,
            "items": [
                {"name": "", "price": 25000, "qty": 1},       # Lỗi tên trống
                {"name": "Cà phê đen", "price": 25000, "qty": -5} # Lỗi số lượng âm
            ]
        }
        response = self.client.post(reverse('add_order'), data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Không có món hợp lệ")
        # Xác nhận đơn hàng lỗi không được phép tồn lưu lại trong cơ sở dữ liệu
        self.assertFalse(Order.objects.filter(booking=self.booking).exists())

    def test_add_order_not_logged_in(self):
        """Testcase 7: Chặn hành vi gọi món khi tài khoản chưa thực hiện đăng nhập hệ thống (View)"""
        self.client.logout() # Đăng xuất tài khoản
        payload = {"booking_id": self.booking.id, "items": [{"name": "Trà Vải", "price": 30000, "qty": 1}]}
        response = self.client.post(reverse('add_order'), data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 302)

    def test_add_order_invalid_booking_id(self):
        """Testcase 8: Hệ thống bảo mật chặn hành vi truyền mã lịch đặt phòng không tồn tại (View)"""
        payload = {"booking_id": 9999, "items": [{"name": "Trà Vải", "price": 30000, "qty": 1}]}
        response = self.client.post(reverse('add_order'), data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 404)

    def test_add_order_method_not_allowed(self):
        """Testcase 9: Chặn và trả mã lỗi 405 khi cố tình tiếp cận bằng phương thức GET (View)"""
        response = self.client.get(reverse('add_order'))
        self.assertEqual(response.status_code, 405)

    def test_add_order_skips_invalid_item_but_saves_valid_ones(self):
        """Testcase 10: Tự động loại bỏ các món lỗi và chỉ tiến hành lưu trữ các món hợp lệ (View)"""
        payload = {
            "booking_id": self.booking.id,
            "items": [
                {"name": "Cà phê sữa", "price": 25000, "qty": 2}, # Món hợp lệ
                {"name": "", "price": 15000, "qty": 0}            # Món lỗi sẽ bị bỏ qua
            ]
        }
        response = self.client.post(reverse('add_order'), data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(booking=self.booking)
        # Kiểm tra chi tiết món gọi kèm chỉ chứa đúng 1 phần tử hợp lệ được lưu
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, "Cà phê sữa")