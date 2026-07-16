from django.conf import settings
from django.db import models


class Photo(models.Model):
    """Модель фотографии в галерее SnapX."""

    CATEGORY_CHOICES = [
        ('nature', 'Природа'),
        ('city', 'Город'),
        ('people', 'Люди'),
        ('other', 'Другое'),
    ]

    title = models.CharField('Название', max_length=200)
    image = models.ImageField('Изображение', upload_to='photos/%Y/%m/%d/')
    category = models.CharField(
        'Категория', max_length=20, choices=CATEGORY_CHOICES, default='other'
    )
    description = models.TextField('Описание', blank=True)

    # Автор привязан к системной модели пользователя.
    # settings.AUTH_USER_MODEL используется вместо прямой ссылки на User —
    # это стандартная практика Django на случай кастомной модели пользователя.
    # on_delete=CASCADE: если пользователь удалён — удаляются и его фото.
    # Если нужно сохранять фото удалённых пользователей, замените на
    # models.SET_NULL и добавьте null=True.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Автор',
    )

    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']  # новые фото — сверху
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return f'{self.title} ({self.author.username})'