from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderItem
from .models import Booking
from apps.boxes.models import Box

@login_required
def book_box(request, box_id):
    box = get_object_or_404(Box, id=box_id)
    
    if request.method == 'POST':
        start = request.POST.get('start_time')
        duration = int(request.POST.get('duration'))
        
        # Chuyển đổi chuỗi thời gian sang object datetime
        start_dt = parse_datetime(start)
        
        # QUAN TRỌNG: Đảm bảo start_dt có thông tin múi giờ
        if timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt)
            
        # So sánh với timezone.now() (luôn là aware)
        if start_dt < timezone.now():
            messages.error(request, "Không thể đặt lịch trong quá khứ!")
            return redirect('home')

        end_dt = start_dt + timedelta(hours=duration)
        
        # Kiểm tra trùng lịch (sử dụng end_dt đã được làm chuẩn)
        overlapping = Booking.objects.filter(
            box=box, status__in=['pending', 'confirmed', 'active', 'cancellation_pending']
        ).filter(Q(start_time__lt=end_dt) & Q(end_time__gt=start_dt))
        
        if overlapping.exists():
            messages.error(request, "Box đã bị đặt trong khung giờ này!")
        else:
            Booking.objects.create(customer=request.user, box=box, start_time=start_dt, end_time=end_dt, status='pending')
            box.status = 'pending'
            box.save(update_fields=['status'])
            messages.success(request, "Yêu cầu đặt box đã được gửi, vui lòng chờ admin/staff phê duyệt.")
            
        return redirect('home')
    return render(request, 'bookings/book.html', {'box': box})


from .models import Booking

def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    orders = Order.objects.filter(booking=booking).prefetch_related('items').order_by('-created_at')
    items = OrderItem.objects.filter(order__in=orders)
    
    # 1. Tính tiền phòng (ví dụ dựa trên đơn giá mỗi giờ của box)
    # Lưu ý: Đây là ví dụ đơn giản, bạn có thể cần logic tính thời gian thực tế
    duration_hours = 1 # Hoặc logic tính giờ của bạn
    booking_fee = duration_hours * booking.box.price_per_hour
    
    # 2. Tính tiền món
    order_total = sum(order.total_price for order in orders)
    
    # 3. Tổng cộng
    grand_total = booking_fee + order_total
    
    # Tính thành tiền từng món (như đã hướng dẫn trước)
    for item in items:
        item.total_item_price = item.price * item.quantity
        
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'orders': orders,
        'items': items,
        'order_total': order_total,
        'booking_fee': booking_fee,    # Truyền tiền phòng sang
        'grand_total': grand_total     # Truyền tổng cộng sang
    })
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import SupportRequest, Booking

@login_required # Thêm decorator để đảm bảo request.user luôn tồn tại
def send_support_request(request, booking_id):
    if request.method == 'POST':
        #Thêm customer=request.user để bảo mật, chỉ chủ phòng mới tìm thấy đơn này
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        message = request.POST.get('message')
        
        if message:
            SupportRequest.objects.create(booking=booking, message=message)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập nội dung'}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ'}, status=400)


@login_required
def request_booking_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if request.method != 'POST':
        return redirect('home')

    if booking.status not in {'pending', 'confirmed'}:
        messages.error(request, "Chỉ có thể yêu cầu hủy đơn đang chờ phê duyệt hoặc chờ check-in.")
        return redirect('home')

    reason = request.POST.get('reason', '').strip()
    if not reason:
        messages.error(request, "Vui lòng chọn lý do hủy đơn.")
        return redirect('home')

    booking.cancellation_previous_status = booking.status
    booking.status = 'cancellation_pending'
    booking.cancellation_reason = reason
    booking.cancellation_requested_at = timezone.now()
    booking.cancellation_response_message = ''
    booking.save(update_fields=[
        'status',
        'cancellation_reason',
        'cancellation_requested_at',
        'cancellation_previous_status',
        'cancellation_response_message',
    ])
    booking.box.status = 'pending'
    booking.box.save(update_fields=['status'])
    messages.success(request, "Yêu cầu hủy của bạn đã được nhận, chúng tôi sẽ xử lý trong 15 phút.")
    return redirect('home')
