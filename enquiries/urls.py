from django.urls import path
from . import views

urlpatterns = [
    path('', views.enquiry_page, name='enquiry_page'),
]
