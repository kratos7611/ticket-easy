from django.urls import path
from . import views

app_name = 'event'

urlpatterns = [
    path("superadmin/dashboard", views.dashboard, name='dashboard'),
    path("superadmin/events", views.dashboard_events, name='dashboard_events'),
    path("superadmin/create_event", views.create_event, name='create_event'),
    path("superadmin/update_event/<int:event_id>/", views.update_event, name='update_event'),
    path("superadmin/delete_event/<int:event_id>/", views.delete_event, name='delete_event'),
    path("explore_events", views.explore_events, name='explore_events'),
]
