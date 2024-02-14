from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path("superadmin/bookings", views.dashboard_bookings, name='dashboard_bookings'),
    path("bookings/", views.my_bookings, name='my_bookings'),
    path("bookings/<int:booking_id>/", views.get_booking_by_id, name='get_booking_by_id'),
    path("bookings/json/<int:booking_id>/", views.get_booking_by_id_json, name='get_booking_by_id_json'),
    path("bookings/cancel/<int:booking_id>/", views.cancel_pending_booking, name='cancel_pending_booking'),
    path("bookings/use/<int:booking_id>/", views.mark_booking_as_used, name='mark_booking_as_used'),
    path('book_now/', views.book_now, name='book_now'),
    path('booking/payment/cancel/', views.payment_cancel_url, name='payment_cancel_url'),
    path('booking/payment/success/<int:booking_id>/', views.payment_success_url,name='payment_success_url'),
]
