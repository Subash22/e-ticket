from django.contrib import admin
from .models import *

# Register your models here.
class BostonStudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email'
    ]
    list_filter = ['full_name', 'email']
    search_fields = ['full_name', 'email']


class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'image_tag',
        'full_name',
        'program',
        'semester',
        'shift',
        'student_email'
    ]
    list_filter = ['program', 'semester', 'shift']
    search_fields = ['full_name', 'program']


class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_id',
        'checked_in',
        'checked_in_date',
        'checked_out',
        'checked_out_date'
    ]
    list_filter = ['ticket_id', 'checked_in', 'checked_out']
    search_fields = ['ticket_id']


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_verified']
    search_fields = ['username', 'email']
    list_filter = ['is_verified']

    class Meta:
        model = CustomUser


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BostonStudent, BostonStudentAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Ticket, TicketAdmin)

