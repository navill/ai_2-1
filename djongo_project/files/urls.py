from django.urls import path

from files.api.views import FileView, download

app_name = 'files'
urlpatterns = [
    path('upload/', FileView.as_view()),
    path('upload/', FileView.as_view(), name='upload'),
    path('upload/<int:pk>', FileView.as_view(), name='file_detail'),
    path('download/<str:path>', download, name='download'),
]
