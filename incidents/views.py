import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Incident, IncidentVerification, Comment, Alert
from .forms import IncidentForm, CommentForm


def _apply_incident_filters(incidents, category='', status='', severity='', search=''):
    """Apply shared incident filters used by list and API views."""
    if category:
        incidents = incidents.filter(category=category)
    if status:
        incidents = incidents.filter(status=status)
    if severity:
        incidents = incidents.filter(severity=severity)
    if search:
        incidents = incidents.filter(
            Q(title__icontains=search) | Q(description__icontains=search) | Q(address__icontains=search)
        )
    return incidents


def home_view(request):
    """Landing page."""
    if request.user.is_authenticated:
        return redirect('incident_list')

    recent_incidents = Incident.objects.all()[:5]
    total_incidents = Incident.objects.count()
    resolved_count = Incident.objects.filter(status='resolved').count()
    total_users = User.objects.count()

    context = {
        'recent_incidents': recent_incidents,
        'total_incidents': total_incidents,
        'resolved_count': resolved_count,
        'total_users': total_users,
    }
    return render(request, 'incidents/home.html', context)


@login_required
def incident_list_view(request):
    """List all incidents with filtering."""
    incidents = Incident.objects.all()

    # Filters
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    severity = request.GET.get('severity', '')
    search = request.GET.get('search', '')

    incidents = _apply_incident_filters(
        incidents,
        category=category,
        status=status,
        severity=severity,
        search=search,
    )

    context = {
        'incidents': incidents,
        'category_filter': category,
        'status_filter': status,
        'severity_filter': severity,
        'search_query': search,
        'categories': Incident.CATEGORY_CHOICES,
        'statuses': Incident.STATUS_CHOICES,
        'severities': Incident.SEVERITY_CHOICES,
    }
    return render(request, 'incidents/incident_list.html', context)


@login_required
def live_incidents_api(request):
    """API endpoint for real-time incidents with optional nearby filtering."""
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    severity = request.GET.get('severity', '')
    search = request.GET.get('search', '')

    incidents = Incident.objects.annotate(
        comment_total=Count('comments', distinct=True),
        verification_total=Count('verifications', filter=Q(verifications__is_verified=True), distinct=True),
    )
    incidents = _apply_incident_filters(
        incidents,
        category=category,
        status=status,
        severity=severity,
        search=search,
    )

    raw_lat = request.GET.get('latitude')
    raw_lng = request.GET.get('longitude')
    raw_radius = request.GET.get('radius_km', '5')
    latitude = None
    longitude = None
    location_applied = False

    try:
        radius_km = float(raw_radius)
        if radius_km <= 0:
            radius_km = 5.0
    except (TypeError, ValueError):
        radius_km = 5.0

    try:
        if raw_lat is not None and raw_lng is not None:
            latitude = float(raw_lat)
            longitude = float(raw_lng)
            location_applied = True
    except (TypeError, ValueError):
        latitude = None
        longitude = None
        location_applied = False

    payload = []
    for incident in incidents[:100]:
        distance_km = None
        if location_applied:
            if incident.latitude is None or incident.longitude is None:
                continue
            distance_km = _haversine_distance(
                latitude,
                longitude,
                incident.latitude,
                incident.longitude,
            )
            if distance_km > radius_km:
                continue

        payload.append({
            'id': incident.pk,
            'title': incident.title,
            'description': incident.description,
            'category': incident.category,
            'category_display': incident.get_category_display(),
            'severity': incident.severity,
            'severity_display': incident.get_severity_display(),
            'status': incident.status,
            'status_display': incident.get_status_display(),
            'time_since': incident.time_since,
            'address': incident.address,
            'comment_count': getattr(incident, 'comment_total', incident.comment_count),
            'verification_count': getattr(incident, 'verification_total', incident.verification_count),
            'photo_url': incident.photo.url if incident.photo else None,
            'media_reference': incident.photo.name if incident.photo else '',
            'detail_url': reverse('incident_detail', kwargs={'pk': incident.pk}),
            'distance_km': round(distance_km, 2) if distance_km is not None else None,
        })

    return JsonResponse({
        'incidents': payload,
        'count': len(payload),
        'location_applied': location_applied,
        'radius_km': radius_km,
    })


@login_required
def incident_detail_view(request, pk):
    """View incident details with comments and verification."""
    incident = get_object_or_404(Incident, pk=pk)
    comments = incident.comments.all()
    verifications = incident.verifications.all()
    user_verified = incident.verifications.filter(verified_by=request.user).exists()
    comment_form = CommentForm()
    verification_count = incident.verification_count
    threshold = settings.VERIFICATION_THRESHOLD

    if threshold and threshold > 0:
        verification_progress = round((verification_count / threshold) * 100)
    else:
        verification_progress = 0
    verification_progress = max(0, min(verification_progress, 100))

    context = {
        'incident': incident,
        'comments': comments,
        'verifications': verifications,
        'user_verified': user_verified,
        'comment_form': comment_form,
        'verification_count': verification_count,
        'threshold': threshold,
        'verification_progress': verification_progress,
    }
    return render(request, 'incidents/incident_detail.html', context)


def _haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def _create_alerts_for_nearby_users(incident):
    """Create alerts for users within their alert radius of the incident."""
    if incident.latitude is None or incident.longitude is None:
        return

    from accounts.models import UserProfile
    profiles = UserProfile.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(user=incident.reported_by)

    for profile in profiles:
        distance = _haversine_distance(
            incident.latitude, incident.longitude,
            profile.latitude, profile.longitude
        )
        if distance <= profile.alert_radius_km:
            Alert.objects.get_or_create(
                incident=incident,
                user=profile.user
            )


@login_required
def report_incident_view(request):
    """Report a new incident."""
    if request.method == 'POST':
        form = IncidentForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            _create_alerts_for_nearby_users(incident)
            messages.success(request, 'Incident reported successfully! Nearby users have been alerted.')
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm()
    return render(request, 'incidents/report.html', {'form': form})


@login_required
def verify_incident_view(request, pk):
    """Verify or dispute an incident."""
    incident = get_object_or_404(Incident, pk=pk)

    if incident.reported_by == request.user:
        messages.warning(request, "You cannot verify your own incident.")
        return redirect('incident_detail', pk=pk)

    if incident.verifications.filter(verified_by=request.user).exists():
        messages.info(request, "You have already submitted verification for this incident.")
        return redirect('incident_detail', pk=pk)

    if request.method == 'POST':
        is_verified = request.POST.get('action') == 'verify'
        notes = request.POST.get('notes', '')
        IncidentVerification.objects.create(
            incident=incident,
            verified_by=request.user,
            is_verified=is_verified,
            notes=notes
        )

        # Auto-verify if threshold reached
        if incident.verification_count >= settings.VERIFICATION_THRESHOLD:
            incident.status = 'verified'
            incident.save()

        action_text = "verified" if is_verified else "disputed"
        messages.success(request, f'You have {action_text} this incident.')
        return redirect('incident_detail', pk=pk)

    return redirect('incident_detail', pk=pk)


@login_required
def add_comment_view(request, pk):
    """Add a comment to an incident."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.incident = incident
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
    return redirect('incident_detail', pk=pk)


@login_required
def alerts_view(request):
    """View user alerts."""
    alerts = Alert.objects.filter(user=request.user)
    unread_count = alerts.filter(is_read=False).count()
    context = {
        'alerts': alerts,
        'unread_count': unread_count,
    }
    return render(request, 'incidents/alerts.html', context)


@login_required
def mark_alert_read_view(request, pk):
    """Mark an alert as read."""
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    alert.is_read = True
    alert.save()
    return redirect('incident_detail', pk=alert.incident.pk)


@login_required
def mark_all_alerts_read_view(request):
    """Mark all alerts as read."""
    Alert.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All alerts marked as read.')
    return redirect('alerts')


@login_required
def get_unread_alert_count(request):
    """API endpoint for unread alert count (for polling)."""
    count = Alert.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@staff_member_required
def admin_dashboard_view(request):
    """Admin dashboard with analytics."""
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)

    total_incidents = Incident.objects.count()
    total_users = User.objects.count()
    incidents_this_month = Incident.objects.filter(created_at__gte=last_30_days).count()
    incidents_this_week = Incident.objects.filter(created_at__gte=last_7_days).count()
    resolved_incidents = Incident.objects.filter(status='resolved').count()
    verified_incidents = Incident.objects.filter(status='verified').count()

    # Category breakdown
    category_data = Incident.objects.values('category').annotate(count=Count('id'))
    # Severity breakdown
    severity_data = Incident.objects.values('severity').annotate(count=Count('id'))
    # Status breakdown
    status_data = Incident.objects.values('status').annotate(count=Count('id'))

    # Recent incidents
    recent_incidents = Incident.objects.all()[:10]

    # Daily incidents for last 30 days
    daily_incidents = []
    for i in range(30):
        day = now - timedelta(days=29 - i)
        count = Incident.objects.filter(
            created_at__date=day.date()
        ).count()
        daily_incidents.append({
            'date': day.strftime('%b %d'),
            'count': count
        })

    # Top reporters
    top_reporters = User.objects.annotate(
        incident_count=Count('incidents')
    ).order_by('-incident_count')[:5]

    context = {
        'total_incidents': total_incidents,
        'total_users': total_users,
        'incidents_this_month': incidents_this_month,
        'incidents_this_week': incidents_this_week,
        'resolved_incidents': resolved_incidents,
        'verified_incidents': verified_incidents,
        'category_data': list(category_data),
        'severity_data': list(severity_data),
        'status_data': list(status_data),
        'recent_incidents': recent_incidents,
        'daily_incidents': daily_incidents,
        'top_reporters': top_reporters,
        'resolution_rate': round(resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0,
    }
    return render(request, 'incidents/admin_dashboard.html', context)


@staff_member_required
def resolve_incident_view(request, pk):
    """Admin action to resolve an incident."""
    incident = get_object_or_404(Incident, pk=pk)
    incident.status = 'resolved'
    incident.save()
    messages.success(request, f'Incident "{incident.title}" has been marked as resolved.')
    return redirect('incident_detail', pk=pk)

@login_required
def delete_incident_view(request, pk):
    """Delete an incident. Allowed for staff or the reporter."""
    incident = get_object_or_404(Incident, pk=pk)
    if not (request.user.is_staff or request.user == incident.reported_by):
        messages.error(request, 'You do not have permission to delete this incident.')
        return redirect('incident_detail', pk=pk)
    
    if request.method == 'POST':
        title = incident.title
        incident.delete()
        messages.success(request, f'Incident "{title}" was successfully deleted.')
        return redirect('incident_list')
        
    return render(request, 'incidents/incident_confirm_delete.html', {'incident': incident})

@staff_member_required
def delete_user_view(request, pk):
    """Admin action to permanently delete a user."""
    user_to_delete = get_object_or_404(User, pk=pk)
    
    if user_to_delete == request.user:
        messages.error(request, 'You cannot delete yourself from the dashboard.')
        return redirect('admin_dashboard')
        
    if user_to_delete.is_superuser:
        messages.error(request, 'You cannot delete a superuser from the dashboard.')
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'User {username} was successfully deleted.')
        return redirect('admin_dashboard')
        
    return render(request, 'incidents/user_confirm_delete.html', {'user_to_delete': user_to_delete})
