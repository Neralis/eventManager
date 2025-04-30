import logging
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from src.apps.userApp.utils import user_avatar_path
from src.utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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
        default='',
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


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        max_length=255,
        validators=[FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg'],
            message='Вы можете использовать только файлы с расширениями PNG и JPEG.'
        )],
        verbose_name='Аватар'
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание профиля'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

    def save(self, *args, **kwargs):
        old_avatar = None
        if self.id:
            old_instance = self.__class__.objects.get(id=self.id)
            old_avatar = old_instance.avatar
            if old_avatar != self.avatar:
                FileHandler.delete_old_image(self, self.__class__, 'avatar')
        if self.avatar and (not old_avatar or old_avatar != self.avatar):
            FileHandler.save_file(
                instance=self,
                file_field_name='avatar',
                path_function=user_avatar_path,
            )
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f'Ошибка при сохранении профиля пользователя: {e}')
            if self.avatar:
                FileHandler.delete_user_folder(self.user.id)
            raise

    def delete(self, *args, **kwargs):
        FileHandler.delete_user_folder(self.id)
        super().delete(*args, **kwargs)


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
        max_length=500,
        verbose_name='Ссылка',
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
            models.Index(fields=['phone']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'phone'],
                name='unique_email_phone'
            )
        ]

    def __str__(self):
        return self.email
