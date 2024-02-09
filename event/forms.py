from django import forms
from django.forms.widgets import DateTimeInput
from .models import Event
from user.models import User


class EventForm(forms.ModelForm):
    organizer = forms.ModelChoiceField(queryset=User.objects.filter(is_organizer=True),
                                       label='Organizer', empty_label=None)

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
            'organizer',
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
            'organizer': forms.Select(attrs={'class': 'form-control h_40'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizer'].widget.attrs['class'] = 'form-control h_40'
        self.fields['organizer'].label_from_instance = self.label_from_user_instance
        self.fields['organizer'].choices = [('', 'Select Organizer')] + list(self.fields['organizer'].choices)

    def label_from_user_instance(self, obj):
        return obj.get_full_name()
