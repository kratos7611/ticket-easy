import random
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse

from .forms import SignUpForm, SignInForm, CustomPasswordResetForm, ChangePasswordForm, CreateUserForm, UpdateUserForm
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
    search_query = request.GET.get('search', '')

    if search_query:
        # Filter users based on the search query
        filtered_users = User.objects.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(
                email__icontains=search_query))
    else:
        # If no search query, get all users
        filtered_users = User.objects.all()

    # Paginate the filtered users
    paginator = Paginator(filtered_users, 8)  # Adjust the number of users per page as needed
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page)

    form = CreateUserForm()
    context = {
        'form': form,
        'users': page_obj,
        'search_query': search_query,
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
                if user.is_superuser:
                    return redirect('event:dashboard')
                elif user.is_organizer:
                    return redirect('event:organizer_dashboard')
                else:
                    return redirect('user:index')
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


@login_required(login_url='user:signin')
@path_checker
def create_user(request):
    show_create_modal = False
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                # Add an error message
                show_create_modal = True
                messages.error(request, 'This email is already registered. Please use a different email.')
            else:
                # Set the email as the username
                form.instance.username = email

                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                # Create a new user
                user = form.save(commit=False)
                user.set_password(password)

                # Set the user role based on the selected role in the form
                role = form.cleaned_data.get('role')
                if role == 'superadmin':
                    user.is_superuser = True
                elif role == 'organizer':
                    user.is_organizer = True
                user.save()
                # Send email with the generated password and login URL
                login_url = request.build_absolute_uri(reverse('user:signin'))
                email_message = f'Your account has been created.\n\nUsername: {user.email}\nPassword: {password}\n\nPlease login at: {login_url}'
                send_mail(
                    'Account Creation',
                    email_message,
                    'info.ticketeasy@gmail.com',
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'User created successfully!')
                return redirect('user:dashboard_users')
        else:
            show_create_modal = True

    else:
        form = CreateUserForm()

    context = {'form': form, 'show_create_modal': show_create_modal}
    return render(request, 'dashboard_users.html', context)


@login_required(login_url='user:signin')
@path_checker
def update_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    show_update_modal = False

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            # Get cleaned data from the form
            cleaned_data = form.cleaned_data
            # Extract necessary fields
            first_name = cleaned_data.get('first_name')
            middle_name = cleaned_data.get('middle_name')
            last_name = cleaned_data.get('last_name')
            gender = cleaned_data.get('gender')

            # Update user instance with extracted data
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.gender = gender

            # Save the updated user
            user.save()

            messages.success(request, 'User updated successfully.')
            return redirect('user:dashboard_users')
        else:
            show_update_modal = True
            errors = form.errors.get_json_data(escape_html=False)
            for field, error_list in errors.items():
                for error in error_list:
                    field_name = form.fields[field].label
                    messages.error(request, f'Validation Error for {field_name}: {error["message"]}')
    else:
        form = UpdateUserForm(instance=user)
        show_update_modal = True

        all_user = User.objects.all()
        paginator = Paginator(all_user, 8)
        page = request.GET.get('page')
        if page is None:
            page = 1
        else:
            show_update_modal = False
        users = paginator.get_page(page)
        users.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {'form': form, 'user': user, 'users': users, 'show_update_modal': show_update_modal}
    return render(request, 'dashboard_users.html', context)


@login_required(login_url='user:signin')
@path_checker
def delete_user(request, user_id):
    event = get_object_or_404(User, id=user_id)
    event.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('user:dashboard_users')
