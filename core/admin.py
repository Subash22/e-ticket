from django.contrib import admin
from core.models import BostonStudent, Student, Ticket

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
        'email'
    ]
    list_filter = ['first_name', 'last_name', 'program', 'semester', 'shift']
    search_fields = ['first_name', 'last_name']


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


admin.site.register(BostonStudent, BostonStudentAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Ticket, TicketAdmin)