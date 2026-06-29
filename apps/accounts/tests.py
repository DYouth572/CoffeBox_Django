from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsModelTestCase(TestCase):
    """1. KIỂM THỬ MODEL USER (Phân quyền và cấu trúc dữ liệu)"""

    def test_create_user_with_default_role(self):
        """Testcase 1: Kiểm tra tạo user thường với vai trò mặc định"""
        user = User.objects.create_user(username="customer1", password="CoffeeBox@2026_Secure!")
        self.assertEqual(user.role, "customer")
        self.assertEqual(str(user), "customer1")

    def test_create_staff_user(self):
        """Testcase 2: Kiểm tra tạo tài khoản nhân viên phân quyền staff"""
        staff_user = User.objects.create_user(username="staff1", password="CoffeeBox@2026_Secure!", role="staff")
        self.assertEqual(staff_user.role, "staff")


class AccountsViewsTestCase(TestCase):
    """2. KIỂM THỬ VIEWS (Xử lý logic giao diện Đăng ký, Đăng nhập, Hồ sơ)"""

    def setUp(self):
        self.strong_password = "CoffeeBox@2026_Secure!"
        self.test_user = User.objects.create_user(username="existinguser", password=self.strong_password)

    def test_register_success(self):
        """Testcase 3: Đăng ký tài khoản mới thành công"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': self.strong_password,
            'password2': self.strong_password
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        """Testcase 4: Chặn đăng ký khi trùng tên username đã có"""
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'password1': self.strong_password,
            'password2': self.strong_password
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_register_missing_fields(self):
        """Testcase 5: Chặn đăng ký khi để trống thông tin bắt buộc"""
        response = self.client.post(reverse('register'), {
            'username': '',
            'password1': '',
            'password2': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Testcase 6: Đăng nhập thành công với đúng tài khoản mật khẩu"""
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': self.strong_password
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        """Testcase 7: Từ chối đăng nhập khi điền sai mật khẩu"""
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'wrong_password_here'
        })
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_username(self):
        """Testcase 8: Từ chối đăng nhập khi username không tồn tại"""
        response = self.client.post(reverse('login'), {
            'username': 'non_existent_user',
            'password': self.strong_password
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_requires_login(self):
        """Testcase 9: Chặn người dùng chưa đăng nhập tiếp cận trang sửa hồ sơ"""
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_success(self):
        """Testcase 10: Cho phép chỉnh sửa hồ sơ thành công"""
        # Đăng nhập hệ thống
        self.client.login(username="existinguser", password=self.strong_password)
        
        # ĐÃ SỬA: Bổ sung trường 'username' bắt buộc vào payload để Form passes validation
        payload = {
            'username': self.test_user.username,
            'first_name': 'Coffee',
            'last_name': 'Box User',
            'email': 'user@coffeebox.com',
            'phone': '0123456789'
        }
        response = self.client.post(reverse('profile_edit'), payload)
        
        # ĐÃ SỬA: Đổi kỳ vọng thành 302 vì khi Form hợp lệ, view sẽ thực hiện redirect sang trang khác
        self.assertEqual(response.status_code, 302)
        
        # Đồng bộ và xác thực dữ liệu đã ghi nhận vào DB
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, 'Coffee')