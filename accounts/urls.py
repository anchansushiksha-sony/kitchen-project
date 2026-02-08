from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_home, name='account_home'),
]
