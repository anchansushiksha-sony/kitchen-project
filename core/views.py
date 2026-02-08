from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.conf import settings
from .forms import RatingForm
from products.models import Product, Category, Rating
from core.models import Wishlist, Order, OrderItem, OrderAddress
from django.db import transaction

import razorpay
from django.contrib.auth import get_user_model

User = get_user_model()

# Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# -------------------- HOME --------------------
def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:4]
    new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]  # latest products

    return render(request, 'core/index.html', {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
    })



# -------------------- STATIC PAGES --------------------
def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == "POST":
        messages.success(request, "Thank you! Your message has been sent.")
        return redirect("contact")
    return render(request, "core/contact.html")


# -------------------- PRODUCTS --------------------




# -------------------------
def products(request):
    products = Product.objects.filter(is_active=True)
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    return render(request, 'core/products.html', {
        'products': products,
        'wishlist_products': wishlist_products,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    ratings = product.ratings.all()
    avg_rating = ratings.aggregate(average=Avg('value'))['average'] or 0
    avg_rating = round(avg_rating, 1)

    user_rating = None
    form = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
        if request.method == 'POST':
            form = RatingForm(request.POST, instance=user_rating)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.product = product
                rating.user = request.user
                rating.save()
                return redirect('product_detail', product_id=product.id)
        if not form:
            form = RatingForm(instance=user_rating)

    return render(request, 'core/product_detail.html', {
        'product': product,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'form': form,
        'user_rating': user_rating,
        'star_range': range(1, 6),
    })


def product_search(request):
    query = request.GET.get('q', '').strip()
    results = Product.objects.filter(is_active=True)
    if query:
        results = results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    return render(request, 'core/search_results.html', {'query': query, 'results': results})

def product_view(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})

# -------------------- AUTH --------------------
""" def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid credentials")
    return render(request, "core/login.html") """


""" def register(request):
    return render(request, "core/register.html")
 """

def logout_view(request):
    logout(request)
    return redirect("home")


# -------------------- CART (SESSION BASED) --------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart

    return redirect('cart')


@login_required
def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * qty
        total += subtotal
        items.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        })

    return render(request, "core/cart.html", {
        "products": items,
        "total_price": total
    })


@login_required
def cart_increase(request, product_id):
    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart
    return redirect("cart")


@login_required
def cart_decrease(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            cart.pop(str(product_id))
    request.session["cart"] = cart
    return redirect("cart")


@login_required
def cart_remove(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart")


# -------------------- CHECKOUT --------------------
@login_required(login_url='login')
@transaction.atomic
def checkout(request):
    cart = request.session.get("cart", {})
    total = 0

    # Calculate total
    for pid, qty in cart.items():
        pid = int(pid)  # 🔥 FIX #1
        product = get_object_or_404(Product, id=pid)
        total += product.price * qty

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=payment_method,
            payment_status=(payment_method == "ONLINE"),
            order_status="PAID" if payment_method == "ONLINE" else "PENDING"
        )

        # Save address
        OrderAddress.objects.create(
            order=order,
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address")
        )

        # Save order items
        for pid, qty in cart.items():
            pid = int(pid)  # 🔥 FIX #2
            product = get_object_or_404(Product, id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )

        # Clear cart
        request.session["cart"] = {}

        return redirect("order_success")

    return render(request, "core/checkout.html", {
        "total": total,
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
    })

# -------------------- RAZORPAY --------------------
@login_required
def create_payment(request):
    cart = request.session.get("cart", {})
    total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        total += product.price * qty

    razorpay_order = razorpay_client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    request.session["razorpay_amount"] = total
    return JsonResponse(razorpay_order)


@login_required
def verify_payment(request):
    total = request.session.get("razorpay_amount")

    Order.objects.create(
        user=request.user,
        total_amount=total,
        payment_method="ONLINE",
        payment_status=True,
        order_status="PAID"
    )

    request.session["cart"] = {}
    request.session.pop("razorpay_amount", None)

    return redirect("order_success")


# --------------------
# CATEGORIES
# --------------------
def categories(request):
    categories = Category.objects.all()
    return render(request, 'core/categories.html', {'categories': categories})


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.filter(is_active=True)

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    return render(request, 'core/category_products.html', {
        'category': category,
        'products': products,
        'wishlist_products': wishlist_products,
    })

    

def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'core/categories.html', {
        'categories': categories
    })


@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    request.session['cart'] = {str(product_id): 1}
    return redirect('checkout')


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )

    # Redirect back to wishlist page
    return redirect('wishlist_page')


@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'core/wishlist.html', context)





#Cstmr lgn/rgstr

def customer_register(request):
    # If already logged in → go home
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
            return redirect('customer_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists. Please login.")
            return redirect('customer_login')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.phone = phone
        user.save()

        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('home')

    return render(request, 'users/register.html')


def customer_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid credentials")

    return render(request, "users/login.html")




@login_required
def order_success(request):
    return render(request, "core/order_success.html")
