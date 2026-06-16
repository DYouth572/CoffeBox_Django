from django.urls import path

from . import admin_views

urlpatterns = [
    path("", admin_views.dashboard, name="admin_dashboard"),
    path("revenue/", admin_views.revenue_history, name="admin_revenue_history"),
    path("bookings/", admin_views.bookings, name="admin_bookings"),
    path("bookings/<int:booking_id>/status/", admin_views.update_booking_status, name="admin_booking_status"),
    path("boxes/", admin_views.boxes, name="admin_boxes"),
    path("boxes/add/", admin_views.save_box, name="admin_box_add"),
    path("boxes/<int:box_id>/edit/", admin_views.save_box, name="admin_box_edit"),
    path("boxes/<int:box_id>/delete/", admin_views.delete_box, name="admin_box_delete"),
    path("products/", admin_views.products, name="admin_products"),
    path("products/add/", admin_views.save_product, name="admin_product_add"),
    path("products/<int:product_id>/edit/", admin_views.save_product, name="admin_product_edit"),
    path("products/<int:product_id>/delete/", admin_views.delete_product, name="admin_product_delete"),
    path("orders/", admin_views.orders, name="admin_orders"),
    path("orders/<int:order_id>/status/", admin_views.update_order_status, name="admin_order_status"),
    path("supports/<int:support_id>/resolve/", admin_views.resolve_support, name="admin_support_resolve"),
    path("users/", admin_views.users, name="admin_users"),
    path("users/<int:user_id>/role/", admin_views.update_user_role, name="admin_user_role"),
]
