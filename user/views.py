from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import SignUpForm, SignInForm, CustomPasswordResetForm, ChangePasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login

User = get_user_model()


def index(request):
    context = {
    }
    return render(request, 'index.html', context)


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
                return redirect('user:index')  # Replace 'index' with the desired URL after successful login
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
