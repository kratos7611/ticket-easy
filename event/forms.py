from django import forms
from django.forms.widgets import DateTimeInput
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'start_datetime',
            'end_datetime',
            'address',
            'about',
            'link',
            'thumbnail_image',
            'issued_ticket_quantity',
            'booked_ticket_quantity',
            'price_per_ticket',
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control h_40'}),
            'start_datetime': DateTimeInput(
                attrs={'class': 'form-control datetimepicker-input', 'type': 'datetime-local'}),
            'end_datetime': DateTimeInput(
                attrs={'class': 'form-control datetimepicker-input', 'type': 'datetime-local'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea'}),
            'about': forms.Textarea(attrs={'class': 'form-textarea'}),
            'link': forms.TextInput(attrs={'class': 'form-control h_40'}),
            'thumbnail_image': forms.FileInput(attrs={'class': 'form-control h_40', 'type': 'file'}),
            'issued_ticket_quantity': forms.NumberInput(attrs={'class': 'form-control h_40'}),
            'booked_ticket_quantity': forms.NumberInput(attrs={'class': 'form-control h_40'}),
            'price_per_ticket': forms.NumberInput(attrs={'class': 'form-control h_40'}),
        }
