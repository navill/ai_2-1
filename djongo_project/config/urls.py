from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.api.urls')),
    path('api/data_upload/', include('data_upload.api.urls'))
]
