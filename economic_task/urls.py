"""economic_task URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from ui.views import method404
from django.conf.urls.static import static
from economic_task import settings

urlpatterns = [
    # default urls
    path('admin/', admin.site.urls),
    # framework urls
    path('api-auth/', include('rest_framework.urls')),
    # applications urls
    path('', include('ui.urls')),
    path('quotes/', include('quotes.urls'))
]

if settings.DEBUG: # Appending urls on local machine
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = method404
