"""
URL configuration for campus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from .views import FrontendAppView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/profile/', include('campusprofile.urls')),
    path('api/shop/', include('Shop.urls')),
    path('api/logistics/', include('Logistics.urls')),
    path('api/reviewhub/', include('ReviewHub.urls')),
    path('api/orders/', include('orders.urls')),
    # re_path("")

    re_path(r'^(?!media/)(?:.*)/?$', FrontendAppView.as_view(),
            name='frontend'),  # catch-all for React
    # re_path(r'^.*$', FrontendAppView.as_view(),
    #         name='frontend'),  # catch-all for React
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
