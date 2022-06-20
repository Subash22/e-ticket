from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('generate-ticket', GenerateTicketView.as_view(), name='generate_ticket'),

    path('check-validation/<str:ticket_id>', check_validation_view, name='check_validation')
]
