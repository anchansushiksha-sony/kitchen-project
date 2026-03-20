from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from core.models import Wishlist, Order, OrderItem
from .models import Product, Category


def products(request):
    products = Product.objects.filter(is_active=True)

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    return render(request, 'products.html', {
        'products': products,
        'wishlist_products': wishlist_products,
    })


def product_search(request):
    query = request.GET.get('q', '')
    price_range = request.GET.get('price')
    category = request.GET.get('category')

    products = Product.objects.filter(is_active=True)

    # 🔍 Keyword search
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # 🏷️ Category filter
    if category:
        products = products.filter(category_id=category)

    # 💰 Price filter
    if price_range and '-' in price_range:
        try:
            min_price, max_price = map(int, price_range.split('-'))

            price_filtered = products.filter(
                price__gte=min_price,
                price__lte=max_price
            )

            if price_filtered.exists():
                products = price_filtered

        except:
            pass
        
    print(products)

    # 📄 Pagination (IMPORTANT)
    paginator = Paginator(products, 6)  # 6 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'core/search_results.html', {
        'products': products_page,          # ✅ paginator object
        'query': query,
        'price_range': price_range,
        'category': category,
        'categories': Category.objects.all()  # ✅ REQUIRED for dropdown
    })

def product_list(request):
    products = Product.objects.all()

    return render(request, 'core/product_list.html', {
        'products': products
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    wishlist_products = []

    return render(request, 'core/product_detail.html', {
        'product': product,
        'wishlist_products': wishlist_products,
    })


@login_required(login_url='users:login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    order, created = Order.objects.get_or_create(
        user=request.user,
        order_status="Pending"
    )

    item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect(request.GET.get("next", "/products/"))