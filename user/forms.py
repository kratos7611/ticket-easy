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


class CreateUserForm(forms.ModelForm):
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
    gender = forms.ChoiceField(choices=[('', 'Choose Gender')] + GENDER_CHOICES, required=True,
                               widget=forms.Select(attrs={'class': 'form-control h_50'}),
                               label='Gender')
    is_superuser = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=False)
    is_organizer = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=False)

    role = forms.ChoiceField(choices=[('superadmin', 'Superadmin'), ('organizer', 'Organizer')],
                             required=False, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                             label='Role')

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'gender', 'role')


class UpdateUserForm(forms.ModelForm):
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
    gender = forms.ChoiceField(choices=[('', 'Choose Gender')] + GENDER_CHOICES, required=True,
                               widget=forms.Select(attrs={'class': 'form-control h_50'}),
                               label='Gender')

    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'gender')
