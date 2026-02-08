from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
# Admin (ONLY ONE)
    path('admin/', admin.site.urls),

 # Home & pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
  # Products
    path('products/', include('products.urls')),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.product_search, name='product_search'),

    # Categories
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),

    # Cart & Orders
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:product_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<int:product_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),

    # Wishlist
     path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    # Checkout & payment
    path('checkout/', views.checkout, name='checkout'),
    path('create-payment/', views.create_payment, name='create_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),


 # Auth (CUSTOMER)
    path('accounts/', include('users.urls')),


#cstmr lgn/rgstr
    path('login/', views.customer_login, name='customer_login'),
    path('register/', views.customer_register, name='customer_register'),
    path('logout/', views.logout_view, name='logout'),
    path('order-success/', views.order_success, name='order_success'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)