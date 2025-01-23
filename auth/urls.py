from django.urls import path
from . import views

urlpatterns = [
    #path('update/', views.update_profile, name='update_profile'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
