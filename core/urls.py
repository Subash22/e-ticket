from django.urls import path
from .views import *
from django.urls import re_path as url
from django.views.static import serve 
from django.conf import settings


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
    path('', HomeView.as_view(), name='home'),
    path('upload-information', UploadInformationView.as_view(), name='upload_information'),
    path('boston', BostonLoginView.as_view(), name='boston'),
    path('update-information', UpdateInformationView.as_view(), name='update_information'),
    path('generate-ticket', GenerateTicketView.as_view(), name='generate_ticket'),
    
    path('activate/<uidb64>/<token>/', activate, name='activate'),

    path('check-validation/<str:ticket_id>', check_validation_view, name='check_validation')
]
