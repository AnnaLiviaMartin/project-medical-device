"""
URL configuration for config project.

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
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve as serve_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("patients.urls")),
    path("api/", include("imaging.urls")),
    path("api/", include("ml.urls")),
]

# Hinweis: In einer groesseren Produktivumgebung wuerde man Media-Dateien
# ueber einen dedizierten Webserver oder Blob-Storage ausliefern statt
# ueber Django. Bei der hier zu erwartenden Last (wenige Zugriffe/Tag)
# ist die direkte Auslieferung durch Django voellig ausreichend und
# spart die zusaetzliche Infrastruktur - daher unabhaengig von DEBUG.
#
# WICHTIG: Der frueher hier verwendete django.conf.urls.static.static()-
# Shortcut sieht zwar so aus, als wuerde er das leisten - er registriert
# aber intern GAR KEINE Route, sobald DEBUG=False ist (das ist in Django
# so fest verdrahtet, static() ist nur fuer die lokale Entwicklung
# gedacht). Da wir hier bewusst mit DJANGO_DEBUG=False produktiv fahren,
# rufen wir die dahinterliegende serve()-View direkt und unconditional auf.
urlpatterns += [
    re_path(
        r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
        serve_media,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
