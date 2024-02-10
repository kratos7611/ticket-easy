import os
import uuid
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import EventForm
from .models import Event
from booking.models import Booking
from ticketeasy.decorators import onauthenticated_user, path_checker


@path_checker
def dashboard(request):
    # Calculate total price sum and total quantity count from the Booking model
    total_price_sum = Booking.objects.exclude(status='CANCELED').aggregate(total_price_sum=Sum('total_price'))[
        'total_price_sum']
    total_quantity_count = Booking.objects.exclude(status='CANCELED').aggregate(total_quantity_count=Sum('quantity'))[
        'total_quantity_count']

    # Calculate total active events and total events from the Event model
    now = timezone.now()

    # Filter active events
    total_active_events = Event.objects.filter(
        end_datetime__gt=now, booked_ticket_quantity__lt=models.F('issued_ticket_quantity')
    ).count()

    total_events = Event.objects.count()

    context = {
        'total_price_sum': total_price_sum,
        'total_quantity_count': total_quantity_count,
        'total_active_events': total_active_events,
        'total_events': total_events,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='user:signin')
@path_checker
def organizer_dashboard(request):
    organizer = request.user  # Assuming the logged-in user is the organizer
    booking = None

    search_query = request.GET.get('search', '')
    if search_query:
        try:
            booking = Booking.objects.get(barcode=search_query, event__organizer=organizer)
        except Booking.DoesNotExist:
            messages.error(request, "Booking not found for the provided barcode")

    # Calculate total price sum excluding canceled bookings
    total_price_sum = Booking.objects.filter(
        event__organizer=organizer
    ).exclude(status='CANCELED').aggregate(total_price_sum=Sum('total_price'))['total_price_sum']

    # Calculate total quantity count excluding canceled bookings
    total_quantity_count = Booking.objects.filter(
        event__organizer=organizer
    ).exclude(status='CANCELED').aggregate(total_quantity_count=Sum('quantity'))['total_quantity_count']

    # Calculate total active events and total events organized by the organizer
    now = timezone.now()

    # Filter active events organized by the organizer
    total_active_events = Event.objects.filter(
        organizer=organizer,
        end_datetime__gt=now,
        booked_ticket_quantity__lt=models.F('issued_ticket_quantity')
    ).count()

    # Total events organized by the organizer
    total_events = Event.objects.filter(organizer=organizer).count()

    context = {
        'booking': booking,
        'search_query': search_query,
        'total_price_sum': total_price_sum,
        'total_quantity_count': total_quantity_count,
        'total_active_events': total_active_events,
        'total_events': total_events,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='user:signin')
@path_checker
def dashboard_events(request):
    # Get the search query from the form
    search_query = request.GET.get('search', '')

    # Filter events based on the search query
    if search_query:
        # Use Q objects to perform a case-insensitive search on the 'title' field
        filtered_events = Event.objects.filter(Q(title__icontains=search_query))
    else:
        # If no search query, get all events
        filtered_events = Event.objects.all()

    # Paginate the filtered events
    paginator = Paginator(filtered_events, 2)
    page = request.GET.get('page', 1)
    events = paginator.get_page(page)
    events.adjusted_elided_pages = paginator.get_elided_page_range(page)

    # Create an instance of the EventForm
    form = EventForm()

    # Add the search query to the context for displaying in the template
    context = {
        'form': form,
        'events': events,
        'search_query': search_query,
    }
    return render(request, 'dashboard_events.html', context)


@login_required(login_url='user:signin')
@path_checker
def organizer_dashboard_events(request):
    # Get the search query from the form
    search_query = request.GET.get('search', '')

    # Filter events based on the search query and the current logged-in user
    if search_query:
        # Use Q objects to perform a case-insensitive search on the 'title' field
        filtered_events = Event.objects.filter(
            Q(title__icontains=search_query) & Q(organizer=request.user)
        )
    else:
        # If no search query, get all events associated with the current user
        filtered_events = Event.objects.filter(organizer=request.user)

    # Paginate the filtered events
    paginator = Paginator(filtered_events, 2)
    page = request.GET.get('page', 1)
    events = paginator.get_page(page)
    events.adjusted_elided_pages = paginator.get_elided_page_range(page)

    # Add the search query to the context for displaying in the template
    context = {
        'events': events,
        'search_query': search_query,
    }
    return render(request, 'dashboard_events.html', context)


def explore_events(request):
    # Get the search query from the form
    search_query = request.GET.get('search', '')

    # Filter events based on the search query
    if search_query:
        # Use Q objects to perform a case-insensitive search on the 'title' field
        filtered_events = Event.objects.filter(Q(title__icontains=search_query))
    else:
        # If no search query, get all events
        filtered_events = Event.objects.all()

    # Paginate the filtered events
    paginator = Paginator(filtered_events, 8)
    page = request.GET.get('page', 1)
    events = paginator.get_page(page)
    events.adjusted_elided_pages = paginator.get_elided_page_range(page)

    # Create an instance of the EventForm
    form = EventForm()

    # Add the search query to the context for displaying in the template
    context = {
        'form': form,
        'events': events,
        'search_query': search_query,
    }
    return render(request, 'explore_events.html', context)


@login_required(login_url='user:signin')
@path_checker
def create_event(request):
    show_create_modal = False
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)

            # Generate a unique ID
            unique_id = str(uuid.uuid4())[:8]

            # Get the uploaded file
            uploaded_file = request.FILES['thumbnail_image']

            # Extract the file extension
            file_extension = os.path.splitext(uploaded_file.name)[1]

            # Construct a unique filename with the generated ID and original file extension
            unique_filename = f"{unique_id}_{event.title}{file_extension}"  # Modify this based on your requirements
            event.thumbnail_image = os.path.join('event_thumbnails', unique_filename)

            # Save the event with the unique filename
            event.save()

            # Save the uploaded file with the unique filename in the MEDIA_ROOT directory
            destination_path = os.path.join(settings.MEDIA_ROOT, 'event_thumbnails', unique_filename)
            with open(destination_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Additional logic, if any
            messages.success(request, 'Event created successfully.')
            return redirect('event:dashboard_events')
        else:
            show_create_modal = True

    else:
        form = EventForm()

    context = {'form': form, 'show_create_modal': show_create_modal}
    return render(request, 'dashboard_events.html', context)


@login_required(login_url='user:signin')
@path_checker
def update_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        messages.error(request, 'Event not found.')
        return redirect('event:dashboard_events')

    show_update_modal = False
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            # Handle thumbnail_image if a new file is uploaded
            if 'thumbnail_image' in request.FILES:
                # Generate a unique ID
                unique_id = str(uuid.uuid4())[:8]

                # Get the uploaded file
                uploaded_file = request.FILES['thumbnail_image']

                # Extract the file extension
                file_extension = os.path.splitext(uploaded_file.name)[1]

                # Construct a unique filename with the generated ID and original file extension
                unique_filename = f"{unique_id}_{event.title}{file_extension}"

                # Save the uploaded file with the unique filename in the MEDIA_ROOT directory
                destination_path = os.path.join(settings.MEDIA_ROOT, 'event_thumbnails', unique_filename)
                with open(destination_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Update the event's thumbnail_image field with the new filename
                event.thumbnail_image = os.path.join('event_thumbnails', unique_filename)

            form.save()

            messages.success(request, 'Event updated successfully.')
            return redirect('event:dashboard_events')
        else:
            show_update_modal = True

    else:
        form = EventForm(instance=event)
        show_update_modal = True

        all_events = Event.objects.all()
        paginator = Paginator(all_events, 2)
        page = request.GET.get('page')
        if page is None:
            page = 1
        else:
            show_update_modal = False
        events = paginator.get_page(page)
        events.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {'form': form, 'event': event, 'events': events, 'show_update_modal': show_update_modal}
    return render(request, 'dashboard_events.html', context)


@login_required(login_url='user:signin')
@path_checker
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('event:dashboard_events')


def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Get the IDs of all events excluding the current event
    all_event_ids_except_current = Event.objects.exclude(id=event.id).values_list('id', flat=True)

    # Choose 8 random event IDs
    random_event_ids = random.sample(list(all_event_ids_except_current), min(8, len(all_event_ids_except_current)))

    # Retrieve the corresponding events
    random_events = Event.objects.filter(id__in=random_event_ids)

    context = {'event': event, 'events': random_events}
    return render(request, 'event_details.html', context)
