from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('incidents/', views.incident_list_view, name='incident_list'),
    path('api/incidents/live/', views.live_incidents_api, name='live_incidents_api'),
    path('incidents/report/', views.report_incident_view, name='report_incident'),
    path('incidents/<int:pk>/', views.incident_detail_view, name='incident_detail'),
    path('incidents/<int:pk>/verify/', views.verify_incident_view, name='verify_incident'),
    path('incidents/<int:pk>/comment/', views.add_comment_view, name='add_comment'),
    path('incidents/<int:pk>/resolve/', views.resolve_incident_view, name='resolve_incident'),
    path('incidents/<int:pk>/delete/', views.delete_incident_view, name='delete_incident'),
    path('dashboard/user/<int:pk>/delete/', views.delete_user_view, name='delete_user'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('alerts/<int:pk>/read/', views.mark_alert_read_view, name='mark_alert_read'),
    path('alerts/read-all/', views.mark_all_alerts_read_view, name='mark_all_alerts_read'),
    path('api/alerts/unread-count/', views.get_unread_alert_count, name='unread_alert_count'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
