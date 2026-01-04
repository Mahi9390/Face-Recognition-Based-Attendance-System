from django.contrib import admin
from .models import StudentData

@admin.register(StudentData)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'roll',
        'get_username',
        'get_email',
        'course',
        'stream',
        'year',
        'present_days',
        'total_days'
    )

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"
