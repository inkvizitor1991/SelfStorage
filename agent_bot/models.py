from django.db import models

class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в сети',
        unique=True
    )
    name = models.CharField(
        'Псевдоним',
        max_length=10
    )
    first_name = models.CharField(
        'Имя пользователя',
        blank=True,
        max_length=10
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        null=True,
        blank=True,
        max_length=10
    )
    phone = models.CharField(
        'Телефон пользователя',
        blank=True,
        max_length=20,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Order(models.Model):
    profile = models.ForeignKey(
        'Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        'Время получения',
        auto_now_add=True
    )

    def __str__(self):
        return f'Заказ {self.pk} от {self.profile}'

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'
