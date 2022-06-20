from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from .models import *
import uuid
from django.contrib import messages
import qrcode
import qrcode.image.svg
from io import BytesIO


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
            boston_student = BostonStudent.objects.filter(full_name=full_name, email=email)
            if boston_student.exists():
                return redirect("generate_ticket")
            messages.error(self.request, "Full-name or email didn't match.")
            return redirect("home")
        except:
            messages.error(self.request, "Something went wrong.")
            return redirect("home")

            
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

            student = Student()
            student.first_name = first_name
            student.last_name = last_name
            student.semester = semester
            student.shift = shift
            student.program = program
            student.email = email
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

