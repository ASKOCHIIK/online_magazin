from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        'Генерация 6-значного кода'
        user.confirmation_code = get_random_string(6, '0123456789')
        user.is_active = False  # гарантируем, что пользователь не активен до подтверждения
        user.save()

        'Отправка письма с кодом (пока через консоль)'
        send_mail(
            'Код подтверждения email',
            f'Ваш код: {user.confirmation_code}',
            'no-reply@config.local',
            [user.email],
        )
        return user


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
