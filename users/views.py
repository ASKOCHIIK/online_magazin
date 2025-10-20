from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, VerifyCodeSerializer
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class VerifyEmailCodeView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if user.confirmation_code == code:
            user.is_active = True
            user.is_email_verified = True
            user.confirmation_code = ''
            user.save()
            return Response({'success': True, 'message': 'Email подтверждён!'})
        else:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)
