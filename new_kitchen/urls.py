from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Core pages (home, etc.)
    path('', include('core.urls')),

    # Products
    path('products/', include('products.urls')),

    # Users (login, register, profile)
    path('users/', include('users.urls')),

    # Authentication
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(next_page='/'),
        name='logout'
    ),
]

# ✅ MEDIA FILES (IMAGES) – THIS IS CORRECT
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )