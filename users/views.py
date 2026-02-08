from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm
from .models import User


def home(request):
    return render(request, 'users/home.html')


# ---------------- CUSTOMER LOGIN ----------------
def customer_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and not user.is_staff:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))

        messages.error(request, "Invalid  username or password")

    return redirect('home')


# ---------------- CUSTOMER REGISTER ----------------
def customer_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('users:customer_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists. Please login.")
            return redirect('users:customer_login')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        

        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('home')

    return render(request, 'users/register.html')

# ---------------- ADMIN LOGIN ----------------
def admin_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user and user.is_staff:
            login(request, user)
            return redirect('/admin/')
        else:
            messages.error(request, "Invalid admin login")

    return redirect('home')


def logout_user(request):
    logout(request)
    return redirect('home')



# Registration
# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect('home')

#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserRegisterForm()

#     return render(request, 'core/register.html', {'form': form})


# Login
# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('home')

#     if request.method == 'POST':
#         form = UserLoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserLoginForm()

#     return render(request, 'core/login.html', {'form': form})


#Logout
# @login_required
# def logout_view(request):
#     logout(request)
#     messages.success(request, "You have been logged out.")
#     return redirect('login')