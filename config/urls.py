"""
URL configuration for store_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = 'WavHaven Administration'  # Default: "Django Administration"
admin.site.site_title = 'WavHaven Admin Portal'     # Default: "Django site admin"
admin.site.index_title = 'Welcome to WavHaven Admin'  # Default: "Site administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', CreateView.as_view(
        template_name='registration/register.html',
        form_class=UserCreationForm,
        success_url='/'
    ), name='register'),
    # Store URLs - must be last to avoid conflicts
    path('', include('store.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
