from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'phone', 'alert_radius_km', 'created_at']
    search_fields = ['user__username', 'location', 'phone']
