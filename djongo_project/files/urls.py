from django.urls import path

from files.api.views import FileView, download_view, FileUploadView

app_name = 'files'
urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('upload/list/', FileView.as_view(), name='file_list'),
    path('upload/<int:pk>', FileView.as_view(), name='file_detail'),
    path('download/<str:path>', download_view, name='download'),
]
