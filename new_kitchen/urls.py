from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView  # <- add this
from core import views  # or your other apps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),

    path('products/', include('products.urls')),
    path('accounts/', include('accounts.urls')),

  # 🔐 authentication (REQUIRED)
    path(
    'login/',
    auth_views.LoginView.as_view(template_name='users/login.html'),
    name='login'
),


    path(
    'logout/',
    LogoutView.as_view(next_page='/'),  # Redirects to home page after logout
    name='logout'
),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
