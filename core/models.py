from django.db import models
from django.utils.html import mark_safe
from e_ticket import settings

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
class BostonStudent(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "Boston Students"



class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError("User should have username")

        if email is None:
            raise TypeError("User should have email")
        

        user = self.model(username=username, email= self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, ):
        if password is None:
            raise TypeError("User should have password")
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        return user



class CustomUser(AbstractBaseUser, PermissionsMixin):
    f_name = models.CharField(blank=True, null=True, max_length=100)
    l_name = models.CharField(blank=True, null=True, max_length=100)
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = CustomUserManager()


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


    def __str__(self):
        return self.username





class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student = models.ForeignKey(BostonStudent, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    semester = models.CharField(max_length=100)
    shift = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    image = models.ImageField(upload_to="students/")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "Students"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    def student_email(self):
        return self.student.email
    
    def image_tag(self):
        if self.image != '':
            return mark_safe('<img src="%s%s" width="150" height="150" />' % (f'{settings.MEDIA_URL}', self.image))


class Ticket(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
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
