from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
    )
    otchestvo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )
    date_birthday = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    phone = PhoneNumberField(
        unique=True,
        verbose_name='Номер телефона'
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_users",
        blank=True,
        verbose_name='Группы'
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_users_permissions",
        blank=True,
        verbose_name='Права пользователя'
    )

    class Meta:
        verbose_name = 'Авторизованный пользователь'
        verbose_name_plural = 'Авторизованные пользователи'

    def __str__(self):
        return f'({self.username}) {self.first_name} {self.last_name} {self.email}'


class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Заголовок уведомления',
        default='Уведомление'
    )
    text = models.TextField(
        verbose_name='Текст уведомления'
    )
    url_event = models.URLField(
        verbose_name='Ссылка'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Статус (Прочитан/Не прочитан)'
    )

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'Уведомление {self.title} для {self.user}'


class NotAuthUser(models.Model):
    email = models.EmailField(
        verbose_name='Почта'
    )
    phone = PhoneNumberField(
        verbose_name='Телефон'
    )

    class Meta:
        verbose_name = 'Неавторизованный пользователь'
        verbose_name_plural = 'Неавторизованные пользователи'
        indexes = [
            models.Index(fields=['email']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'phone'],
                name='unique_email_phone'
            )
        ]

    def __str__(self):
        return self.email
