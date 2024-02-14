import json
import base64

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from event.models import Event
from .models import Booking
from barcode import EAN13
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from ticketeasy.decorators import onauthenticated_user, path_checker

User = get_user_model()


@login_required(login_url='user:signin')
@path_checker
def dashboard_bookings(request):
    search_query = request.GET.get('search', '')

    # Filter bookings based on the search query
    if search_query:
        filtered_bookings = Booking.objects.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__middle_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    else:
        # If no search query, get all bookings
        filtered_bookings = Booking.objects.all()

    # Paginate the filtered bookings
    paginator = Paginator(filtered_bookings, 4)  # Adjust the number of items per page as needed
    page = request.GET.get('page', 1)
    bookings = paginator.get_page(page)
    bookings.adjusted_elided_pages = paginator.get_elided_page_range(page)

    # Add the search query to the context for displaying in the template
    context = {
        'bookings': bookings,
        'search_query': search_query,
    }
    return render(request, 'dashboard_bookings.html', context)


@login_required(login_url='user:signin')
def my_bookings(request):
    search_query = request.GET.get('search', '')

    # Filter bookings based on the search query and the logged-in user
    if search_query:
        filtered_bookings = Booking.objects.filter(
            (Q(user=request.user) &
             (Q(user__first_name__icontains=search_query) |
              Q(user__middle_name__icontains=search_query) |
              Q(user__last_name__icontains=search_query)))
        )
    else:
        # If no search query, get bookings only associated with the logged-in user
        filtered_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')

    # Paginate the filtered bookings
    paginator = Paginator(filtered_bookings, 4)  # Adjust the number of items per page as needed
    page = request.GET.get('page', 1)
    bookings = paginator.get_page(page)
    bookings.adjusted_elided_pages = paginator.get_elided_page_range(page)

    # Add the search query to the context for displaying in the template
    context = {
        'bookings': bookings,
        'search_query': search_query,
    }
    return render(request, 'my_bookings.html', context)


@login_required(login_url='user:signin')
def get_booking_by_id(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    context = {'booking': booking}
    return render(request, 'invoice.html', context)


@login_required(login_url='user:signin')
def get_booking_by_id_json(request, booking_id):
    try:
        booking = Booking.objects.select_related('user', 'event').get(id=booking_id)
        booking_data = {
            'id': booking.id,
            'user_full_name': booking.user.get_full_name(),
            'event_title': booking.event.title,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format the datetime as needed
            'price': booking.price,
            'quantity': booking.quantity,
            'total_price': booking.total_price,
            'status': booking.status,
        }
        return JsonResponse(booking_data)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)


def cancel_pending_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the booking is pending
    if booking.status == 'PENDING':
        event = booking.event
        quantity = booking.quantity
        event.booked_ticket_quantity -= quantity
        event.save()

        # Update booking status to 'CANCELLED'
        booking.status = 'CANCELED'
        booking.save()

        messages.success(request, 'Booking canceled successfully.')
        return redirect('booking:my_bookings')
    else:
        messages.error(request, 'Ooops! Booking cancel Failed.')
        return redirect('booking:my_bookings')


def mark_booking_as_used(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.is_barcode_expired = True
    booking.save()
    messages.success(request, 'Booking has been updated successfully.')
    return redirect('event:organizer_dashboard')


def book_now(request):
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                if request.user.is_superuser or request.user.is_organizer:
                    return JsonResponse({'success': False, 'message': 'Oops! Unauthorized action.'})
                else:
                    # Retrieve data from the frontend
                    user = request.user

                    # Use request.body to get raw JSON data
                    data = json.loads(request.body.decode('utf-8'))
                    event_id = data.get('event_id')
                    quantity = data.get('quantity')

                    # Retrieve event details
                    event = Event.objects.get(id=event_id)
                    price_per_ticket = event.price_per_ticket

                    # Calculate total price
                    total_price = quantity * price_per_ticket

                    # Create a booking record
                    booking = Booking.objects.create(
                        user=user,
                        event=event,
                        quantity=quantity,
                        price=price_per_ticket,
                        total_price=total_price,
                        status='PENDING',
                        # Add other fields as needed
                    )

                    # Generate barcode and save image
                    if not booking.barcode:  # Check if barcode is not already generated
                        # Adjust as needed to create a 13-digit code
                        code = f'{event.id:06d}{booking.id:06d}'

                        # Ensure the code is exactly 12 digits
                        if len(code) != 12:
                            raise ValueError("Invalid barcode length")

                        ean = EAN13(code, writer=ImageWriter())
                        buffer = BytesIO()
                        ean.write(buffer)

                        # Save barcode image
                        image_name = f'barcode_{code}.png'
                        booking.barcode_image.save(image_name, File(buffer), save=True)
                        booking.barcode = ean.get_fullcode()
                        booking.save()  # Save the booking to update barcode_number

                        # Update booked_ticket_quantity in Event
                        event.booked_ticket_quantity += quantity
                        event.save()

                        return JsonResponse({'success': True, 'message': 'Booking successful'})
            else:
                return JsonResponse({'success': False, 'message': 'Please signin first for booking.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def payment_cancel_url(request):
    messages.error(request, "Ooops! Payment has been cancelled.")
    return redirect('booking:my_bookings')

def payment_success_url(request, booking_id):
    base64_response = request.GET.get('data', '')

    # Decode the Base64 string
    decoded_bytes = base64.b64decode(base64_response)
    decoded_string = decoded_bytes.decode('utf-8')

    # Convert the decoded string to a JSON object
    json_data = json.loads(decoded_string)

    status = json_data.get('status')

    if status == 'COMPLETE':
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'COMPLETED'
        booking.save()
        messages.success(request, "Payment received successfully.")
    else:
        messages.error(request, f"Oops! Payment status put on {status}. Contact support team.")

    return redirect('booking:my_bookings')
