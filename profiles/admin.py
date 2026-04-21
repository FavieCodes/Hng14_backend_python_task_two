from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'age', 'age_group', 'country_name', 'created_at']
    list_filter = ['gender', 'age_group', 'country_id']
    search_fields = ['name', 'country_name']
    readonly_fields = ['id', 'created_at']