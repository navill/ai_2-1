from django.urls import path

from files.api.views import FileUploadView

app_name = 'files'
urlpatterns = [
    path('upload/', FileUploadView.as_view())
]
