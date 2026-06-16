import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.bookings.models import Booking
from apps.orders.models import Order, OrderItem


@login_required
@require_POST
def add_order(request):
    data = json.loads(request.body)
    items = data.get("items", [])
    booking_id = data.get("booking_id")

    if not items:
        return JsonResponse({"status": "error", "message": "Giỏ hàng đang trống"}, status=400)

    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    total_price = sum(int(item.get("price", 0)) * int(item.get("qty", 0)) for item in items)

    order = Order.objects.create(
        booking=booking,
        customer=request.user,
        total_price=total_price,
        status="submitted",
    )

    order_items = []
    for item in items:
        quantity = int(item.get("qty", 0))
        price = int(item.get("price", 0))
        product_name = item.get("name", "").strip()
        if quantity <= 0 or not product_name:
            continue
        order_items.append(
            OrderItem(
                order=order,
                product_name=product_name,
                price=price,
                quantity=quantity,
            )
        )

    if not order_items:
        order.delete()
        return JsonResponse({"status": "error", "message": "Không có món hợp lệ"}, status=400)

    OrderItem.objects.bulk_create(order_items)
    return JsonResponse({"status": "success", "order_id": order.id, "total_price": order.total_price})
