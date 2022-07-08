import csv
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from .models import *
import uuid
from django.contrib import messages
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.mail import BadHeaderError, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


UserModel = get_user_model()


# Create your views here.
class HomeView(View):
    def get(self, *args, **kwargs):
        try:
            context = {
                'title': "Boston Festa",
            }
            return render(self.request, "core/index.html", context)
        except:
            return redirect("home")


class BostonLoginView(View):
    def get(self, *args, **kwargs):
        try:
            context = {
                'title': "Boston Festa",
            }
            return render(self.request, "core/login.html", context)
        except:
            return redirect("boston")

    def post(self, *args, **kwargs):
        try:
            full_name = self.request.POST['full_name']
            email = self.request.POST['email']

            boston_student = BostonStudent.objects.filter(full_name__iexact=full_name, email=email).first()
            if boston_student:
                if UserModel.objects.filter(username=email).first():
                    if Ticket.objects.filter(student__user__username=email).first():
                        messages.error(self.request, "Ticket already generated with this email.")
                        return redirect("boston")
                    else:
                        user = UserModel.objects.get(username=email)
                        send_verification_link(self.request, user, Student.objects.get(user=user))
                        context = {
                            "title": "Verification Email Sent"
                        }
                        return render(self.request, "core/verification_sent.html", context)
                context = {
                    'title': "Generate Ticket for Boston Festa",
                    'name': full_name,
                    'email': email
                }
                return render(self.request, "core/update_information.html", context)

            messages.error(self.request, "Full-name or email didn't match.")
            return redirect("boston")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("boston")

            
# class LoginView(View):
#     def get(self, *args, **kwargs):
#         try:
#             context = {
#                 'title': "Boston Festa",
#             }
#             return render(self.request, "core/login.html", context)
#         except:
#             return redirect("home")

#     def post(self, *args, **kwargs):
#         try:
#             email = self.request.POST['email']
#             password = self.request.POST['password']
#             user = UserModel.objects.filter(username=email).first()
#             if user:
#                 if user.is_verified == True:
#                     user = authenticate(self.request, username=email, password=password)
#                     if user is not None:
#                         login(self.request, user)
#                     else:
#                         messages.error(self.request, "Username and password didn't match.")
#                         return redirect("login")
#                 else:
#                     messages.error(self.request, "Please activate your account before login.")
#                     return redirect("login")
#             else:
#                 messages.error(self.request, "Username doesn't exists.")
#                 return redirect("login")
#             return redirect("generate_ticket")
#         except:
#             messages.error(self.request, "Something went wrong.")
#             return redirect("login")

class UploadInformationView(View):

    def get(self, *args, **kwargs):
        try:
            context = {
                'title': "Boston Festa",
            }
            return render(self.request, "core/outside_information.html", context)
        except:
            return redirect("upload_information")

    def post(self, *args, **kwargs):
        try:
            email = self.request.POST['email']
            if UserModel.objects.filter(username=email).first():
                if Ticket.objects.filter(student__user__username=email).first():
                    messages.error(self.request, "Ticket already generated with this email.")
                    return redirect("upload_information")
                else:
                    user = UserModel.objects.get(username=email)
                    send_verification_link(self.request, user, Student.objects.get(user=user))
                    context = {
                        "title": "Verification Email Sent"
                    }
                    return render(self.request, "core/verification_sent.html", context)
            
            try:
                with transaction.atomic():
                    # open an atomic transaction, i.e. all successful or none
                    user = create_user_db(self.request)
                    student = create_outside_student_db(self.request, user)
                    send_verification_link(self.request, user, student)
            except Exception as e:
                print(e)
                messages.error(self.request, "Something went wrong.")
                return redirect("upload_information")

            context = {
                "title": "Verification Email Sent"
            }
            return render(self.request, "core/verification_sent.html", context)
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("upload_information")


def create_outside_student_db(request, user):
    phone = request.POST['phone']
    study = request.POST['higher_study']
    college = request.POST['college_name']
    image = request.FILES['image']

    student = OutsideStudent()
    student.user = user
    student.phone = phone
    student.study = study
    student.college = college
    student.image = image
    student.save()
    return student


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_verified == True:
            messages.error(request,'Email already activated. Check your email for your ticket.')
            return redirect('home')
        user.is_active = True
        user.is_verified = True
        user.save()
        user = UserModel.objects.filter(username=user.username).first()
        if user:
            if user.is_verified == True:
                user = authenticate(request, username=user.username, password=user.username)
                if user is not None:
                    login(request, user)
                else:
                    messages.error(request, "Username and password didn't match.")
                    return redirect("home")
            else:
                messages.error(request, "Please activate your account.")
                return redirect("home")
        # messages.success(request,'Email confirmed. Now you can login your account.')
        return redirect('generate_ticket')
    else:
        messages.error(request,'Invalid or expired link.')
        return redirect('home')


class UpdateInformationView(View):

    def post(self, *args, **kwargs):
        try:
            full_name = self.request.POST['full_name']
            email = self.request.POST['email']
            boston_student = BostonStudent.objects.filter(full_name__iexact=full_name, email=email).first()
            if boston_student:
                if UserModel.objects.filter(username=email).first():
                    if Ticket.objects.filter(student__user__username=email).first():
                        messages.error(self.request, "Ticket already generated with this email.")
                        return redirect("home")
                    else:
                        user = UserModel.objects.get(username=email)
                        send_verification_link(self.request, user, Student.objects.get(user=user))
                        context = {
                            "title": "Verification Email Sent"
                        }
                        return render(self.request, "core/verification_sent.html", context)
                
                try:
                    with transaction.atomic():
                        # open an atomic transaction, i.e. all successful or none
                        user = create_user_db(self.request)
                        student = create_student_db(self.request, user, boston_student)
                        send_verification_link(self.request, user, student)
                except:
                    messages.error(self.request, "Something went wrong.")
                    return redirect("home")

                context = {
                    "title": "Verification Email Sent"
                }
                return render(self.request, "core/verification_sent.html", context)
            else:
                messages.error(self.request, "Full-name or email didn't match.")
                return redirect("home")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("home")


def create_user_db(request):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']

    user = UserModel.objects.create_user(email, email, email)
    # user = UserModel.objects.get(username=email)
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.is_active = False
    user.save()
    return user


def create_student_db(request, user, boston_student):
    semester = request.POST['semester']
    shift = request.POST['shift']
    program = request.POST['program']
    phone = request.POST['phone']
    image = request.FILES['image']

    student = Student()
    student.student = boston_student
    student.user = user
    student.program = program
    student.semester = semester
    student.shift = shift
    student.phone = phone
    student.image = image
    student.save()
    return student


def send_verification_link(request, user, student):
    current_site = get_current_site(request)
    subject = "Verify your email - Boston Festa"
    email_template_name = "core/verify_email.txt"
    c = {
        "email": user.email,
        'domain': current_site,
        'site_name': 'Interface',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "full_name": student.full_name,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',
    }
    email = render_to_string(email_template_name, c)
    send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


class GenerateTicketView(View):

    def get(self, *args, **kwargs):
        try:
            if self.request.user.is_authenticated:
                ticket = Ticket.objects.filter(student__user=self.request.user).first()
                if ticket:
                    context = {
                        'name': ticket.student.full_name,
                        'email': ticket.student.student_email,
                        'created_at': ticket.created_at,
                        'ticket_id': ticket.ticket_id
                    }
                    background = Image.open('core/static/core/images/ticket.png')
                    img = qrcode.make(ticket.ticket_id, box_size=10)
                    img.save('media/qr/'+ticket.ticket_id+'_qr.png')
                    foreground = Image.open('media/qr/'+ticket.ticket_id+'_qr.png')
                    foreground = foreground.resize((290, 290))

                    img = Image.new('RGB', (1192, 483), (250,250,250))
                    img.paste(background,(0,0))
                    img.paste(foreground,(30,70))
                    img.save('media/tickets/'+ticket.ticket_id+'_ticket.png')

                    context["ticket"] = 'media/tickets/'+ticket.ticket_id+'_ticket.png'
                    return render(self.request, "core/save_ticket.html", context)
                elif Ticket.objects.filter(outside_student__user=self.request.user).first():
                    ticket = Ticket.objects.filter(outside_student__user=self.request.user).first()
                    context = {
                        'name': ticket.outside_student.full_name,
                        'email': ticket.outside_student.student_email,
                        'created_at': ticket.created_at,
                        'ticket_id': ticket.ticket_id
                    }
                    background = Image.open('core/static/core/images/ticket.png')
                    img = qrcode.make(ticket.ticket_id, box_size=10)
                    img.save('media/qr/'+ticket.ticket_id+'_qr.png')
                    foreground = Image.open('media/qr/'+ticket.ticket_id+'_qr.png')
                    foreground = foreground.resize((290, 290))

                    img = Image.new('RGB', (1192, 483), (250,250,250))
                    img.paste(background,(0,0))
                    img.paste(foreground,(30,70))
                    img.save('media/tickets/'+ticket.ticket_id+'_ticket.png')

                    context["ticket"] = 'media/tickets/'+ticket.ticket_id+'_ticket.png'
                    return render(self.request, "core/save_ticket.html", context)
                else:
                    student = Student.objects.filter(user=self.request.user).first()
                    if student:
                        ticket = Ticket()
                        ticket.student = student
                        ticket.ticket_id = str(uuid.uuid4())
                        ticket.save()
                        context = {
                            'name': student.full_name,
                            'email': student.student_email,
                            'created_at': ticket.created_at,
                            'ticket_id': ticket.ticket_id
                        }
                        background = Image.open('core/static/core/images/ticket.png')
                        img = qrcode.make(ticket.ticket_id, box_size=10)
                        img.save('media/qr/'+ticket.ticket_id+'_qr.png')
                        foreground = Image.open('media/qr/'+ticket.ticket_id+'_qr.png')
                        foreground = foreground.resize((290, 290))

                        img = Image.new('RGB', (1192, 483), (250,250,250))
                        img.paste(background,(0,0))
                        img.paste(foreground,(30,70))
                        img.save('media/tickets/'+ticket.ticket_id+'_ticket.png')

                        context["ticket"] = 'media/tickets/'+ticket.ticket_id+'_ticket.png'
                        return render(self.request, "core/save_ticket.html", context)
                    elif OutsideStudent.objects.filter(user=self.request.user).first():
                        outside_student = OutsideStudent.objects.filter(user=self.request.user).first()
                        
                        ticket = Ticket()
                        ticket.outside_student = outside_student
                        ticket.ticket_id = str(uuid.uuid4())
                        ticket.save()
                        context = {
                            'name': outside_student.full_name,
                            'email': outside_student.student_email,
                            'created_at': ticket.created_at,
                            'ticket_id': ticket.ticket_id
                        }
                        background = Image.open('core/static/core/images/ticket.png')
                        img = qrcode.make(ticket.ticket_id, box_size=10)
                        img.save('media/qr/'+ticket.ticket_id+'_qr.png')
                        foreground = Image.open('media/qr/'+ticket.ticket_id+'_qr.png')
                        foreground = foreground.resize((290, 290))

                        img = Image.new('RGB', (1192, 483), (250,250,250))
                        img.paste(background,(0,0))
                        img.paste(foreground,(30,70))
                        img.save('media/tickets/'+ticket.ticket_id+'_ticket.png')

                        context["ticket"] = 'media/tickets/'+ticket.ticket_id+'_ticket.png'
                        return render(self.request, "core/save_ticket.html", context)
                    messages.error(self.request, "Student doesn't exists.")
                    return redirect("home")
            else:
                messages.error(self.request, "Login to continue.")
                return redirect("login")
        except Exception as e:
            print(e)
            messages.error(self.request, "Something went wrong.")
            return redirect("home")



def decode_utf8(line_iterator):
    for line in line_iterator:
        yield line.decode('utf-8')


def create_upload(request):
    if request.method == 'POST':
        # Get the correct type string instead of byte without reading full file into memory with a generator to decode line by line
        products_file = csv.reader(decode_utf8(request.FILES['file']))
        next(products_file)  # Skip header row

        for counter, line in enumerate(products_file):
            full_name = line[0]
            email = line[2]

            bs = BostonStudent()
            bs.full_name = full_name
            bs.email = email
            bs.save()

        messages.success(request, 'Saved successfully!')

        return redirect('home')







# Flutter api for checking QR validation
def check_validation_view(request, ticket_id):
    if request.method == "GET":
        try:
            ticket = Ticket.objects.filter(ticket_id=ticket_id).first()
            if ticket:
                context = {
                    'message': 'valid',
                    'name': ticket.student.student.full_name,
                }
                return JsonResponse(context)
            return JsonResponse({'message': 'invalid'}, status=404)
        except:
            return JsonResponse({'message': 'Something went wrong.'}, status=400)
