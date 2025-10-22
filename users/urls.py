from django.urls import path
from .views import RegisterView, VerifyEmailCodeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_email_code/', VerifyEmailCodeView.as_view(), name='verify_email_code'),
]
