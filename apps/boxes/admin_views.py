from decimal import Decimal
from datetime import timedelta, date

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.bookings.models import Booking, SupportRequest
from apps.orders.models import Order, Product
from .models import Box, BoxCategory


def _is_portal_user(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or getattr(user, "role", "") in {"admin", "staff"}
        )
    )


def _is_admin_user(user):
    return user.is_authenticated and (
        user.is_superuser or user.is_staff or getattr(user, "role", "") == "admin"
    )


def portal_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not _is_portal_user(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not _is_admin_user(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def _sync_booking_statuses():
    now = timezone.now()
    no_show_bookings = Booking.objects.select_related("box").filter(
        status="confirmed",
        start_time__lte=now - timedelta(minutes=15),
    )
    for booking in no_show_bookings:
        booking.status = "cancelled"
        booking.cancelled_at = now
        booking.cancellation_note = "Khách không đến check-in sau 15 phút kể từ giờ bắt đầu."
        booking.box.status = "available"
        booking.box.save(update_fields=["status"])
        booking.save(update_fields=["status", "cancelled_at", "cancellation_note"])

    completed_bookings = Booking.objects.select_related("box").filter(status="active", end_time__lte=now)
    for booking in completed_bookings:
        booking.status = "completed"
        booking.box.status = "completed"
        booking.box.save(update_fields=["status"])
        booking.save(update_fields=["status"])


def _booking_fee_today():
    today = timezone.localdate()
    return (
        Booking.objects.filter(created_at__date=today, status__in=["confirmed", "active", "completed"])
        .aggregate(total=Sum("total_price"))
        .get("total")
        or Decimal("0")
    )


def _set_box_status_for_booking(booking):
    if booking.status == "pending":
        booking.box.status = "pending"
    elif booking.status == "confirmed":
        booking.box.status = "confirmed"
    elif booking.status == "active":
        booking.box.status = "active"
    elif booking.status in {"completed", "cancelled"}:
        booking.box.status = "available"
    elif booking.status == "cancellation_pending":
        booking.box.status = "pending"
    booking.box.save(update_fields=["status"])


@portal_required
def dashboard(request):
    _sync_booking_statuses()
    now = timezone.now()
    today = timezone.localdate()
    # Count boxes by their status, not bookings
    active_count = Box.objects.filter(status="active").count()
    total_boxes = Box.objects.count()
    pending_confirmed_boxes = Box.objects.filter(status__in=["pending", "confirmed"]).count()
    order_revenue = (
        Order.objects.filter(created_at__date=today)
        .filter(status__in=["submitted", "preparing", "served"])
        .aggregate(total=Sum("total_price"))
        .get("total")
        or 0
    )

    context = {
        "total_boxes": total_boxes,
        "active_bookings": active_count,
        "pending_bookings": pending_confirmed_boxes,
        "today_revenue": _booking_fee_today() + Decimal(order_revenue),
        "recent_bookings": Booking.objects.select_related("customer", "box")[:8],
        "top_customers": (
            Booking.objects.values("customer__username", "customer__first_name")
            .annotate(count=Count("id"), total=Sum("total_price"))
            .order_by("-count")[:5]
        ),
        "support_requests": SupportRequest.objects.select_related("booking", "booking__box", "booking__customer")
        .filter(is_resolved=False)
        .order_by("-created_at")[:5],
        "submitted_orders": Order.objects.select_related("customer", "booking", "booking__box")
        .prefetch_related("items")
        .exclude(status="served")
        .order_by("-created_at")[:5],
    }
    return render(request, "portal/dashboard.html", context)


@portal_required
def bookings(request):
    _sync_booking_statuses()
    today = timezone.localdate()
    context = {
        "bookings": Booking.objects.select_related("customer", "box").order_by("-created_at"),
        "pending_count": Booking.objects.filter(status="pending").count(),
        "confirmed_count": Booking.objects.filter(status="confirmed").count(),
        "active_count": Booking.objects.filter(status="active").count(),
        "cancellation_pending_count": Booking.objects.filter(status="cancellation_pending").count(),
        "completed_today": Booking.objects.filter(status="completed", end_time__date=today).count(),
    }
    return render(request, "portal/bookings.html", context)


@require_POST
@portal_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    action = request.POST.get("action")
    now = timezone.now()

    if action == "approve" and booking.status == "pending":
        booking.status = "confirmed"
        booking.save(update_fields=["status"])
        _set_box_status_for_booking(booking)
        if booking.is_short_notice:
            messages.warning(request, f"Đã phê duyệt #VAT-{booking.id}, nhưng đơn được tạo sát giờ bắt đầu.")
        else:
            messages.success(request, f"Đã phê duyệt #VAT-{booking.id}.")
        return redirect(request.POST.get("next") or "admin_bookings")

    if action == "checkin" and booking.status == "confirmed":
        booking.status = "active"
        booking.checked_in_at = now
        booking.save(update_fields=["status", "checked_in_at"])
        _set_box_status_for_booking(booking)
        messages.success(request, f"Đã check-in #VAT-{booking.id}. Đồng hồ sử dụng đã bắt đầu.")
        return redirect(request.POST.get("next") or "admin_bookings")

    if action == "confirm_cancel" and booking.status == "cancellation_pending":
        if not booking.cancellation_in_policy:
            messages.error(request, "Yêu cầu hủy ngoài khung 6-24 giờ. Vui lòng từ chối hủy hoặc dùng thao tác admin/staff hủy nếu có ngoại lệ.")
            return redirect(request.POST.get("next") or "admin_bookings")
        booking.status = "cancelled"
        booking.cancelled_at = now
        booking.cancellation_note = request.POST.get("note", "").strip() or "Admin/staff xác nhận hủy."
        booking.save(update_fields=["status", "cancelled_at", "cancellation_note"])
        _set_box_status_for_booking(booking)
        messages.success(request, f"Đã hủy #VAT-{booking.id} và giải phóng box.")
        return redirect(request.POST.get("next") or "admin_bookings")

    if action == "reject_cancel" and booking.status == "cancellation_pending":
        booking.status = booking.cancellation_previous_status or "confirmed"
        booking.cancellation_response_message = request.POST.get("message", "").strip() or "Yêu cầu hủy không được chấp nhận do không đúng chính sách."
        booking.save(update_fields=["status", "cancellation_response_message"])
        _set_box_status_for_booking(booking)
        messages.success(request, f"Đã từ chối yêu cầu hủy #VAT-{booking.id}.")
        return redirect(request.POST.get("next") or "admin_bookings")

    if action == "staff_cancel" and booking.status in {"pending", "confirmed", "active", "cancellation_pending"}:
        booking.status = "cancelled"
        booking.cancelled_at = now
        booking.cancellation_note = request.POST.get("note", "").strip() or "Admin/staff hủy đơn."
        booking.save(update_fields=["status", "cancelled_at", "cancellation_note"])
        _set_box_status_for_booking(booking)
        messages.success(request, f"Đã hủy #VAT-{booking.id} và giải phóng box.")
        return redirect(request.POST.get("next") or "admin_bookings")

    messages.error(request, "Thao tác không hợp lệ với trạng thái hiện tại.")
    return redirect(request.POST.get("next") or "admin_bookings")


@portal_required
def boxes(request):
    return render(
        request,
        "portal/boxes.html",
        {
            "boxes": Box.objects.select_related("category").order_by("name"),
            "categories": BoxCategory.objects.order_by("name"),
        },
    )


@require_POST
@admin_required
def save_box(request, box_id=None):
    box = get_object_or_404(Box, pk=box_id) if box_id else Box()
    category_id = request.POST.get("category")
    box.name = request.POST.get("name", "").strip()
    box.category = BoxCategory.objects.filter(pk=category_id).first() if category_id else None
    box.capacity = int(request.POST.get("capacity") or 1)
    box.price_per_hour = Decimal(request.POST.get("price_per_hour") or "0")
    box.status = request.POST.get("status") or "available"
    box.description = request.POST.get("description", "").strip()
    if request.FILES.get("image"):
        box.image = request.FILES["image"]
    box.save()
    messages.success(request, "Đã lưu thông tin box.")
    return redirect("admin_boxes")


@require_POST
@admin_required
def delete_box(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    box.delete()
    messages.success(request, "Đã xóa box.")
    return redirect("admin_boxes")


@portal_required
def products(request):
    return render(request, "portal/products.html", {"products": Product.objects.order_by("name")})


@require_POST
@admin_required
def save_product(request, product_id=None):
    product = get_object_or_404(Product, pk=product_id) if product_id else Product()
    product.name = request.POST.get("name", "").strip()
    product.price = Decimal(request.POST.get("price") or "0")
    product.stock = int(request.POST.get("stock") or 0)
    product.is_active = request.POST.get("is_active") == "on"
    if request.FILES.get("image"):
        product.image = request.FILES["image"]
    product.save()
    messages.success(request, "Đã lưu sản phẩm.")
    return redirect("admin_products")


@require_POST
@admin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Đã xóa sản phẩm.")
    return redirect("admin_products")


@portal_required
def orders(request):
    return render(
        request,
        "portal/orders.html",
        {
            "orders": Order.objects.select_related("customer", "booking", "booking__box")
            .prefetch_related("items")
            .order_by("-created_at")
        },
    )


@require_POST
@portal_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    status = request.POST.get("status")
    if status not in {"submitted", "preparing", "served"}:
        messages.error(request, "Trạng thái đơn món không hợp lệ.")
        return redirect("admin_orders")
    allowed_transitions = {
        "submitted": {"preparing"},
        "preparing": {"served"},
        "served": set(),
    }
    if status != order.status and status not in allowed_transitions.get(order.status, set()):
        messages.error(request, "Chỉ có thể chuyển đơn theo luồng: Đã gửi → Đang pha chế → Đã phục vụ.")
        return redirect(request.POST.get("next") or "admin_orders")
    order.status = status
    order.save(update_fields=["status"])
    messages.success(request, f"Đã cập nhật đơn món #{order.id}.")
    return redirect(request.POST.get("next") or "admin_orders")


@require_POST
@portal_required
def resolve_support(request, support_id):
    support = get_object_or_404(SupportRequest, pk=support_id)
    support.is_resolved = True
    support.save(update_fields=["is_resolved"])
    messages.success(request, "Đã đánh dấu yêu cầu hỗ trợ là đã xử lý.")
    return redirect(request.POST.get("next") or "admin_dashboard")


@portal_required
def revenue_history(request):
    """Thống kê doanh thu chi tiết theo ngày"""
    # Get date filter from request
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = timezone.localdate()
    else:
        selected_date = timezone.localdate()
    
    # Get all bookings and orders for selected date
    booking_revenue = Booking.objects.filter(
        created_at__date=selected_date,
        status__in=["confirmed", "active", "completed"]
    ).select_related("customer", "box")
    
    order_revenue = Order.objects.filter(
        created_at__date=selected_date,
        status__in=["submitted", "preparing", "served"]
    ).select_related("customer", "booking", "booking__box").prefetch_related("items")
    
    # Calculate totals
    booking_total = booking_revenue.aggregate(total=Sum("total_price")).get("total") or Decimal("0")
    order_total = order_revenue.aggregate(total=Sum("total_price")).get("total") or 0
    total_revenue = booking_total + Decimal(str(order_total))
    
    context = {
        'selected_date': selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'booking_revenue': booking_revenue,
        'order_revenue': order_revenue,
        'booking_total': float(booking_total),
        'order_total': float(order_total),
        'total_revenue': float(total_revenue),
    }
    
    return render(request, "portal/revenue_history.html", context)


@admin_required
def users(request):
    User = get_user_model()
    return render(request, "portal/users.html", {"users": User.objects.order_by("username")})


@require_POST
@admin_required
def update_user_role(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)
    role = request.POST.get("role")
    if role not in {"customer", "staff", "admin"}:
        messages.error(request, "Vai trò không hợp lệ.")
        return redirect("admin_users")
    user.role = role
    user.is_staff = role == "admin"
    user.save(update_fields=["role", "is_staff"])
    messages.success(request, f"Đã cập nhật vai trò cho {user.username}.")
    return redirect("admin_users")
