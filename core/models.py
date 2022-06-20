from django.db import models
from django.utils.html import mark_safe
from e_ticket import settings

# Create your models here.
class BostonStudent(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "Boston Students"


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    semester = models.CharField(max_length=100)
    shift = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    image = models.ImageField(upload_to="students/")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Students"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def image_tag(self):
        if self.image != '':
            return mark_safe('<img src="%s%s" width="150" height="150" />' % (f'{settings.MEDIA_URL}', self.image))


class Ticket(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    ticket_id = models.CharField(max_length=100)
    checked_in = models.BooleanField(default=False)
    checked_in_date = models.DateTimeField(null=True, blank=True)
    checked_out = models.BooleanField(default=False)
    checked_out_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.ticket_id

    class Meta:
        verbose_name_plural = "Tickets"
