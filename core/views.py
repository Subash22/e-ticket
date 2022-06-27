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

            boston_student = BostonStudent.objects.filter(full_name=full_name, email=email).first()
            if boston_student:
                return redirect('generate_ticket')

            messages.error(self.request, "Full-name or email didn't match.")
            return redirect("home")
        except Exception as e:
            print(e)
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
            boston_student = BostonStudent.objects.filter(email=email, password=password)
            if boston_student.exists():
                return redirect("generate_ticket")
            messages.error(self.request, "Email or password didn't match.")
            return redirect("login")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("login")

            
class GenerateTicketView(View):
    def get(self, *args, **kwargs):
        try:
            context = {
                'title': "Generate Ticket for Boston Festa",
            }
            return render(self.request, "core/update_information.html", context)
        except:
            return redirect("generate_ticket")
    
    def post(self, *args, **kwargs):
        try:
            first_name = self.request.POST['first_name']
            last_name = self.request.POST['last_name']
            semester = self.request.POST['semester']
            shift = self.request.POST['shift']
            program = self.request.POST['program']
            email = self.request.POST['email']
            image = self.request.FILES['image']

            student = Student()
            student.first_name = first_name
            student.last_name = last_name
            student.semester = semester
            student.shift = shift
            student.program = program
            student.email = email
            student.image = image
            student.save()

            ticket = Ticket()
            ticket.student = student
            ticket.ticket_id = str(uuid.uuid4())
            ticket.save()
            context = {
                'name': first_name + ' ' + last_name,
                'email': email,
                'created_at': ticket.created_at,
                'ticket_id': ticket.ticket_id
            }
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(ticket.ticket_id, image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            return render(self.request, "core/save_ticket.html", context)
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("generate_ticket")


def check_validation_view(request, ticket_id):
    if request.method == "GET":
        try:
            ticket = Ticket.objects.filter(ticket_id=ticket_id)
            if not ticket.exists():
                return JsonResponse({'message': 'invalid'})
            ticket = ticket.first()
            context = {
                'message': 'valid',
                'name': ticket.student.first_name + ' ' + ticket.student.last_name,
            }
            return JsonResponse(context)
        except:
            return JsonResponse({'message': 'Somethong went wrong.'})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active == True:
            messages.error(request,'Email already confirmed. Please login to your account.')
            return redirect('login')
        user.is_active = True
        user.save()
        messages.success(request,'Email confirmed. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request,'Invalid or expired link.')
        return redirect('login')