from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string
from rest_framework.validators import UniqueValidator

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email уже используется")]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username уже используется")]
    )
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

        # Генерация 8-значного кода
        user.confirmation_code = get_random_string(6, '0123456789')
        user.is_active = False
        user.save()

        # Отправка красивого HTML-письма
        subject = "Добро пожаловать! Подтвердите email"
        from_email = "askatkulmanov1@gmail.com"
        to_email = [user.email]

        text_content = f"""
Привет, {user.username}!
Ваш код для подтверждения email: {user.confirmation_code}
Используйте его для завершения регистрации.
"""

        html_content = f"""
<html>
<body>
  <h2>Привет, {user.username}!</h2>
  <p>Спасибо за регистрацию на нашем сайте.</p>
  <p>Ваш код для подтверждения email:</p>
  <h1 style="font-size: 36px; font-weight: bold; color: #2a9d8f;">
    {user.confirmation_code}
  </h1>
  <p>Используйте его для завершения регистрации.</p>
  <a href="https://fullcode.kg/" style="
      display: inline-block;
      padding: 10px 20px;
      background-color: #2a9d8f;
      color: white;
      font-weight: bold;
      text-decoration: none;
      border-radius: 5px;
  ">Подтвердить email</a>
  <p style="color: gray; font-size: 12px;">Не передавайте код никому. Код действителен 10 минут.</p>
</body>
</html>
"""

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return user


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)