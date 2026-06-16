from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # THÊM DÒNG NÀY VÀO:
    path('profile/', views.profile_edit, name='profile_edit'),
]