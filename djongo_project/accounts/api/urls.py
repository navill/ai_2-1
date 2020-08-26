from django.urls import path

from accounts.api.views import TokenObtainSlidingView, TokenRefreshView, TokenBlackListView, TokenVerifyView, RegisterView

app_name = 'api'

urlpatterns = [
    path('regist/', RegisterView.as_view(), name='regist'),
    path('token/', TokenObtainSlidingView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('token/logout/', TokenBlackListView.as_view(), name='logout'),
    path('token/verify/', TokenVerifyView.as_view(), name='verify')
]
