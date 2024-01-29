from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path("superadmin/bookings", views.dashboard_bookings, name='dashboard_bookings'),
    path('book_now/', views.book_now, name='book_now'),
]
