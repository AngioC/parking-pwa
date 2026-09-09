from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Aggiunto
from django.conf.urls.static import static # Aggiunto

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('parking.urls')),
]

# Aggiungi questa riga per servire i file media durante lo sviluppo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)