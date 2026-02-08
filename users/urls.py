""" from django.urls import path
from . import views
from .views import register_view, login_view, logout_view

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.customer_login, name='customer_login'),
    path('register/', views.customer_register, name='customer_register'),
    path('admin-login/', views.admin_login, name='admin_login'),

    path('logout/', views.logout_user, name='logout'),
] """


# users/urls.py
from django.urls import path
from . import views

app_name = "users"  # IMPORTANT

urlpatterns = [
    path("login/", views.customer_login, name="customer_login"),
    path("register/", views.customer_register, name="customer_register"),
    path("logout/", views.logout_user, name="logout"),
]

