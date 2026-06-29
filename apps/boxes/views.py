from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from apps.bookings.models import Booking
from apps.orders.models import Product
from .models import Box


def _sync_customer_booking_statuses(user):
    now = timezone.now()
    user_bookings = Booking.objects.select_related("box").filter(customer=user).exclude(status__in=["completed", "cancelled"])

    for booking in user_bookings:
        if booking.status == "confirmed" and booking.start_time <= now - timedelta(minutes=15):
            booking.status = "cancelled"
            booking.cancelled_at = now
            booking.cancellation_note = "Khách không đến check-in sau 15 phút kể từ giờ bắt đầu."
            booking.box.status = "available"
            booking.box.save(update_fields=["status"])
            booking.save(update_fields=["status", "cancelled_at", "cancellation_note"])
        elif booking.status == "active" and booking.end_time <= now:
            booking.status = "completed"
            booking.box.status = "completed"
            booking.box.save(update_fields=["status"])
            booking.save(update_fields=["status"])


def home(request):
    role = "Khách hàng"
    my_bookings = []

    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = "Quản trị viên"
        elif getattr(request.user, "role", "") == "staff" or request.user.groups.filter(name="Nhân viên").exists():
            role = "Nhân viên"

        _sync_customer_booking_statuses(request.user)
        my_bookings = (
            Booking.objects.filter(customer=request.user)
            .exclude(status__in=["completed", "cancelled"])
            .order_by("-created_at")
        )

    now = timezone.now()
    busy_box_ids = Booking.objects.filter(
        status__in=["pending", "confirmed", "active", "cancellation_pending"],
        end_time__gte=now,
    ).values_list("box_id", flat=True)

    boxes = Box.objects.exclude(id__in=busy_box_ids)
    products = Product.objects.all()

    return render(
        request,
        "boxes/home.html",
        {
            "boxes": boxes,
            "products": products,
            "role": role,
            "my_bookings": my_bookings,
        },
    )
