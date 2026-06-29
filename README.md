# 📖 README.md 

**Date**: June 4, 2026  


---

<p align="center">
  <a href="https://youtu.be/tkKzp_mt_-c">
    <img src="https://img.youtube.com/vi/tkKzp_mt_-c/maxresdefault.jpg" alt="Watch the Demo Video" width="750">
  </a>
  <br>
  <i>🎬 Nhấp vào hình ảnh để xem video demo chi tiết toàn bộ tính năng hệ thống (Thời lượng: 8 phút)</i>
</p>

## 📋 Sections Added

### 1. **Header & Navigation** 🎯
- Professional header with badges (Django, Python, MySQL, License)
- Quick navigation links to all major sections
- Clean markdown formatting with emojis

### 2. **Tổng Quan (Overview)** 📋
- **Project Description**: 2-giao diện (khách hàng & quản trị)
- **Feature Matrix**: 7 tính năng cho khách, 6 cho nhân viên, 7 cho admin
- **Project Structure**: Chi tiết thư mục với mô tả từng file
  - apps/ structure (accounts, boxes, bookings, orders)
  - config/ (settings, URLs, WSGI)
  - templates/ (portal, app templates)
  - static/ & media/ folders

### 3. **Yêu Cầu Hệ Thống (Requirements)** ⚙️
- **Hardware minimums**: CPU, RAM, Disk
- **Software requirements**: Python 3.8+, Database, Browser
- **Verification commands**: How to check Python & pip version

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT CHI TIẾT (Installation Guide)

### 6 Detailed Steps:

#### **Bước 1: Clone Repository** 📥
- Windows instructions
- macOS/Linux instructions
- Directory structure verification

#### **Bước 2: Create Virtual Environment** 🔧
- **Windows PowerShell** method
- **Windows Command Prompt** method (alternative)
- **macOS/Linux** method
- How to verify successful activation

#### **Bước 3: Install Dependencies** 📦
- pip upgrade step
- requirements.txt installation
- List of packages being installed
- Verification command

#### **Bước 4: Database Configuration** ⚙️
- **SQLite** (default, simplest)
- **MySQL** (advanced):
  - Installation links
  - Database creation script
  - User creation & permissions
  - settings.py updates
  - Running migrations

#### **Bước 5: Create Admin Account** 👤
- `createsuperuser` command
- All prompts explained
- Reminder to save credentials

#### **Bước 6: Verification** ✅
- System check command
- Expected output

---

## 🎬 CHẠY DỰ ÁN (Running the Project)

### Starting Development Server
```bash
python manage.py runserver
```

### Access Points Table
| Address | Purpose |
|---------|---------|
| localhost:8000 | Customer homepage |
| localhost:8000/portal | Admin/Staff dashboard |
| localhost:8000/admin | Django admin panel |
| localhost:8000/login | Login page |
| localhost:8000/register | Registration page |

---

## 📖 HƯỚNG DẪN SỬ DỤNG WEBSITE (User Guides)

### **A. FOR CUSTOMERS** 🎯 (10 Steps)

**1. Đăng Ký Tài Khoản**
- Step-by-step registration process

**2. Đăng Nhập**
- Login instructions

**3. Xem Danh Sách Box**
- What information is displayed
- How to browse available spaces

**4. Đặt Box** ⭐
- Detailed booking flow
- Time selection
- Duration choice
- Price calculation
- Confirmation process
- Status tracking after booking

**5. Gọi Món Khi Đang Ở Box**
- Accessing the orders section
- Adding items to cart
- Quantity adjustment
- Order submission
- Kitchen notification

**6. Theo Dõi Lịch Sử Đặt**
- History section location
- Information displayed
- Filtering & sorting

**7. Yêu Cầu Hủy Đơn**
- When can you cancel
- Cancellation request process
- Status updates

**8. Yêu Cầu Hỗ Trợ**
- How to report issues
- Staff response process

**9. Chỉnh Sửa Hồ Sơ Cá Nhân**
- Profile update fields
- Avatar upload
- Contact info update

**10. Đăng Xuất**
- Logout process

---

### **B. FOR STAFF & ADMIN** 👨‍💼 (7 Sections)

**1. Đăng Nhập Portal**
- Staff/admin login process
- Portal URL

**2. Dashboard Tổng Quan**
- KPI display (total boxes, active, pending, revenue)
- Recent bookings table
- Navigation overview

**3. Quản Lý Đơn Đặt (Bookings)**
- View all bookings
- Approve pending bookings
- Reject bookings (with reason)
- Cancel bookings (with notes)
- Confirm check-in
- Complete bookings

**4. Quản Lý Thực Đơn (Products)**
- View products
- Add new products (name, price, stock, image)
- Edit products
- Delete/disable products

**5. Quản Lý Box**
- View box list
- Status explanations (available, pending, confirmed, active, completed)
- Add new box (name, category, capacity, price/hour, description, image)
- Manage categories

**6. Quản Lý Đơn Gọi Món (Orders)**
- View all orders
- Order status (submitted, preparing, served)
- Update order status based on kitchen progress

**7. Quản Lý Người Dùng (Admin only)**
- View all users
- Assign roles (customer, staff, admin)
- Activate/deactivate accounts

---

### **C. DJANGO ADMIN PANEL** 🛠️
- Access URL
- Login process
- Features: Models management, Permissions, Groups, Site configuration

---

## 🔧 Advanced Configuration

### Environment Variables (.env)
Example file with:
- Django settings
- Database config
- Email configuration
- Other optional settings

### Django Settings Update
Code example for loading from .env

---

## 📊 Data Management

### Backup & Restore
- **SQLite**: File copy method
- **MySQL**: mysqldump commands

### Reset Database
- flush command
- Fresh migrations
- Create new admin account

---

## 🐛 Troubleshooting (6 Common Issues)

**1. ModuleNotFoundError: No module named 'django'**
- Cause: Virtual env not activated
- Solution: Activate venv + reinstall

**2. TemplateDoesNotExist**
- Cause: Missing templates folder
- Solution: Check templates directory

**3. No such table**
- Cause: Migrations not run
- Solution: python manage.py migrate

**4. Permission denied** (.ps1)
- Solution: Set-ExecutionPolicy command

**5. Server won't start**
- Diagnosis: python manage.py check
- Solutions: migrate, use different port

**6. Port 8000 already in use**
- Solution: Use different port (8080, etc.)

---

## 📱 Production Deployment

### Heroku Deployment
- Heroku CLI installation
- Login & create app
- Database setup
- Deploy with git push
- Run migrations
- Create superuser

### VPS/Dedicated Server
- Requirements: Python, Gunicorn, Nginx, PostgreSQL, SSL
- Note: Detailed deployment guide available separately

---

## 📚 Reference Documentation

| Resource | Link |
|----------|------|
| Django Docs | https://docs.djangoproject.com/ |
| Python Docs | https://docs.python.org/3/ |
| Bootstrap | https://getbootstrap.com/docs/ |
| MySQL | https://dev.mysql.com/doc/ |

---

## 👥 Project Info

- **Version**: 1.0.0
- **Python**: 3.8+
- **Django**: 4.2+
- **Database**: SQLite / MySQL
- **License**: MIT
- **Author**: Vạt Coffee Team
- **Date**: June 4, 2026

---

## 📊 Content Statistics

| Section | Lines | Words |
|---------|-------|-------|
| Header & Overview | 50 | 300 |
| Requirements | 30 | 150 |
| Installation (6 steps) | 150 | 800 |
| Running Project | 20 | 100 |
| Customer Guide (10 steps) | 200 | 1200 |
| Staff/Admin Guide (7 steps) | 200 | 1500 |
| Configuration | 50 | 300 |
| Troubleshooting | 80 | 400 |
| Deployment | 40 | 250 |
| FAQ & Contact | 50 | 350 |
| **TOTAL** | **~860** | **~5350** |

---

