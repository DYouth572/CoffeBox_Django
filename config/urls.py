from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('portal/', include('apps.boxes.admin_urls')),
    path('admin/', admin.site.urls),
    
    # Trang chủ map vào app boxes (Đảm bảo trong apps/boxes/urls.py có path('', views.home, name='home'))
    path('', include('apps.boxes.urls')), 
    path('', include('apps.accounts.urls')),
    
    # Đường dẫn xác thực
    path('bookings/', include('apps.bookings.urls')),
    path('orders/', include('apps.orders.urls')),
]

# Cấu hình media để hiển thị ảnh
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
