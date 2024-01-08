from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'

urlpatterns = [
    path("", views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),

    path('reset-password/',
         auth_views.PasswordResetView.as_view(
             template_name="components/forget_password.html",
             email_template_name='components/password_reset_email.html',
             subject_template_name = 'components/password_reset_subject.txt',
             success_url=reverse_lazy('user:password_reset_done'),
             form_class=views.CustomPasswordResetForm
         ),
         name="reset_password"),

    path('reset-password/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="components/password_reset_done.html"
         ),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="components/change_password.html",
             success_url=reverse_lazy('user:password_reset_complete'),
             form_class=views.ChangePasswordForm
         ),
         name="password_reset_confirm"),

    path('reset-password-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="components/password_reset_complete.html"
         ),
         name="password_reset_complete"),
]