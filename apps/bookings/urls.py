from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:box_id>/', views.book_box, name='book_box'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('support/<int:booking_id>/', views.send_support_request, name='send_support_request'),
    path('cancel/<int:booking_id>/', views.request_booking_cancellation, name='request_booking_cancellation'),
    
]
