from django.urls import path

from accounts.api.tokens.views import TokenObtainSlidingView, TokenRefreshView, TokenBlackListView, TokenVerifyView, \
    TestView
from accounts.api.views import RegisterView, StaffRegisterView

app_name = 'api'
urlpatterns = [
    path('regist/', RegisterView.as_view(), name='regist'),
    path('staff_regist/', StaffRegisterView.as_view(), name='staff_regist'),
    path('token/', TokenObtainSlidingView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('token/logout/', TokenBlackListView.as_view(), name='logout'),
    path('token/verify/', TokenVerifyView.as_view(), name='verify'),

    path('test/', TestView.as_view(), name='test')
]
