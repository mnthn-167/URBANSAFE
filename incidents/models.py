from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Incident(models.Model):
    """Model for reporting safety incidents."""

    CATEGORY_CHOICES = [
        ('hazard', 'Safety Hazard'),
        ('emergency', 'Emergency'),
        ('suspicious', 'Suspicious Activity'),
        ('infrastructure', 'Infrastructure Issue'),
        ('other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('verified', 'Verified'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='reported')
    address = models.CharField(max_length=300, help_text="Location address")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    photo = models.ImageField(upload_to='incident_photos/', blank=True, null=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    @property
    def verification_count(self):
        return self.verifications.filter(is_verified=True).count()

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def time_since(self):
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f"{delta.days}d ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours}h ago"
        minutes = delta.seconds // 60
        return f"{minutes}m ago"


class IncidentVerification(models.Model):
    """Verification of an incident by community members."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='verifications')
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    is_verified = models.BooleanField(default=True, help_text="True=confirm, False=dispute")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('incident', 'verified_by')
        verbose_name = "Incident Verification"
        verbose_name_plural = "Incident Verifications"

    def __str__(self):
        status = "Verified" if self.is_verified else "Disputed"
        return f"{self.verified_by.username} {status} '{self.incident.title}'"

    @property
    def time_since(self):
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f"{delta.days}d ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours}h ago"
        minutes = delta.seconds // 60
        return f"{minutes}m ago"


class Comment(models.Model):
    """Comments on incidents for community discussion."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on '{self.incident.title}'"

    @property
    def time_since(self):
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f"{delta.days}d ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours}h ago"
        minutes = delta.seconds // 60
        return f"{minutes}m ago"


class Alert(models.Model):
    """Alerts sent to nearby users about incidents."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='alerts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"

    def __str__(self):
        return f"Alert for {self.user.username}: {self.incident.title}"
