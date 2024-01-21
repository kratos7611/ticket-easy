from django.shortcuts import render


def dashboard_bookings(request):
    context = {
    }
    return render(request, 'dashboard_bookings.html', context)
