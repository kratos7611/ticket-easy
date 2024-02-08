from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import SignUpForm, SignInForm, CustomPasswordResetForm, ChangePasswordForm
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import authenticate, login
from event.models import Event
from ticketeasy.decorators import onauthenticated_user, path_checker

User = get_user_model()


def index(request):
    latest_events = Event.objects.order_by('-start_datetime')[:4]

    context = {
        'latest_events': latest_events,
    }
    return render(request, 'index.html', context)


@path_checker
def dashboard_users(request):
    context = {
    }
    return render(request, 'dashboard_users.html', context)


def unauthorized(request):
    context = {
    }
    return render(request, 'components/unauthorized.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Extract email from the form
            email = form.cleaned_data['email']

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                # Add an error message
                messages.error(request, 'This email is already registered. Please use a different email.')
            else:
                # Set the email as the username
                form.instance.username = email

                # Save the form and create the user
                user = form.save()

                # Add a success message
                messages.success(request, 'Account created successfully. You can now sign in.')

                return redirect('user:signin')

        else:
            messages.error(request, 'Error creating account. Please fix the errors.')
    else:
        form = SignUpForm()

    return render(request, 'components/sign_up.html', {'form': form})


@onauthenticated_user
def signin(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request:
        form = SignInForm(request.POST)

        # Check whether the form is valid:
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Log the user in
                login(request, user)
                # Redirect to a success page.
                # if super admin else index with more menu
                return redirect('event:dashboard')
            else:
                # Return an 'invalid login' error message.
                messages.error(request, 'Invalid email or password.')

    else:
        form = SignInForm()

    context = {'form': form}
    return render(request, 'components/sign_in.html', context)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'components/forget_password.html'
    email_template_name = 'components/password_reset_email.html'
    subject_template_name = 'components/password_reset_subject.txt'
    success_url = reverse_lazy('user:password_reset_done')
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'components/change_password.html'
    success_url = reverse_lazy('user:password_reset_complete')
    form_class = ChangePasswordForm


def signout(request):
    logout(request)
    return redirect('user:index')
