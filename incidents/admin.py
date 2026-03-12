from django.contrib import admin
from .models import Incident, IncidentVerification, Comment, Alert


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'severity', 'status', 'reported_by', 'created_at']
    list_filter = ['category', 'severity', 'status', 'created_at']
    search_fields = ['title', 'description', 'address']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']


@admin.register(IncidentVerification)
class IncidentVerificationAdmin(admin.ModelAdmin):
    list_display = ['incident', 'verified_by', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['incident', 'user', 'text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['incident', 'user', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
