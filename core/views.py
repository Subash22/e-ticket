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

    def post(self, *args, **kwargs):
        try:
            full_name = self.request.POST['full_name']
            email = self.request.POST['email']

            boston_student = BostonStudent.objects.filter(full_name__iexact=full_name, email=email).first()
            if boston_student:
                if UserModel.objects.filter(username=email).first():
                    messages.error(self.request, "Ticket already generated with this email.")
                    return redirect("home")
                context = {
                    'title': "Generate Ticket for Boston Festa",
                    'name': full_name,
                    'email': email
                }
                return render(self.request, "core/update_information.html", context)

            messages.error(self.request, "Full-name or email didn't match.")
            return redirect("home")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("home")

            
class LoginView(View):
    def get(self, *args, **kwargs):
        try:
            context = {
                'title': "Boston Festa",
            }
            return render(self.request, "core/login.html", context)
        except:
            return redirect("home")

    def post(self, *args, **kwargs):
        try:
            email = self.request.POST['email']
            password = self.request.POST['password']
            user = UserModel.objects.filter(username=email).first()
            if user:
                if user.is_verified == True:
                    user = authenticate(self.request, username=email, password=password)
                    if user is not None:
                        login(self.request, user)
                    else:
                        messages.error(self.request, "Username and password didn't match.")
                        return redirect("login")
                else:
                    messages.error(self.request, "Please activate your account before login.")
                    return redirect("login")
            else:
                messages.error(self.request, "Username doesn't exists.")
                return redirect("login")
            return redirect("generate_ticket")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_verified == True:
            messages.error(request,'Email already confirmed. Please login to your account.')
            return redirect('login')
        user.is_active = True
        user.is_verified = True
        user.save()
        messages.success(request,'Email confirmed. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request,'Invalid or expired link.')
        return redirect('login')


class UpdateInformationView(View):

    def post(self, *args, **kwargs):
        try:
            full_name = self.request.POST['full_name']
            email = self.request.POST['email']
            boston_student = BostonStudent.objects.filter(full_name__iexact=full_name, email=email).first()
            if boston_student:
                if UserModel.objects.filter(username=email).first():
                    messages.error(self.request, "Ticket already generated with this email. Login to continue.")
                    return redirect("login")

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
    raw_password = request.POST['password']

    user = UserModel.objects.create_user(email, email, raw_password)
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
    image = request.FILES['image']

    student = Student()
    student.student = boston_student
    student.user = user
    student.program = program
    student.semester = semester
    student.shift = shift
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
                    factory = qrcode.image.svg.SvgImage
                    img = qrcode.make(ticket.ticket_id, image_factory=factory, box_size=10)
                    stream = BytesIO()
                    img.save(stream)
                    context["svg"] = stream.getvalue().decode()
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
                        factory = qrcode.image.svg.SvgImage
                        img = qrcode.make(ticket.ticket_id, image_factory=factory, box_size=10)
                        stream = BytesIO()
                        img.save(stream)
                        context["svg"] = stream.getvalue().decode()
                        return render(self.request, "core/save_ticket.html", context)
                    messages.error(self.request, "Student doesn't exists.")
                    return redirect("home")
            else:
                messages.error(self.request, "Login to continue.")
                return redirect("login")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("home")









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
