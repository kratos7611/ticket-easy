from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordResetForm
from .models import User


class SignUpForm(UserCreationForm):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]

    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control h_50'}))
    middle_name = forms.CharField(max_length=30, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control h_50'}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control h_50'}))
    email = forms.EmailField(max_length=254, required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control h_50'}))
    password1 = forms.CharField(max_length=30, required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control h_50'}),
                                label='Password')
    password2 = forms.CharField(max_length=30, required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control h_50'}),
                                label='Confirm Password')
    gender = forms.ChoiceField(choices=[('', 'Choose Gender')] + GENDER_CHOICES, required=True,
                               widget=forms.Select(attrs={'class': 'form-control h_50'}),
                               label='Gender')

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'password1', 'password2', 'gender')


class SignInForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True,
                             widget=forms.EmailInput(
                                 attrs={'class': 'form-control h_50', 'placeholder': 'Enter your email'}))
    password = forms.CharField(max_length=30, required=True,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control h_50', 'placeholder': 'Enter your password'}))


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control h_50', 'placeholder': 'Enter your email'}),
    )


class ChangePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control h_50', 'placeholder': 'Enter your new password'}),
    )

    new_password2 = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control h_50', 'placeholder': 'Confirm your new password'}),
    )
