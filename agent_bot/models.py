from django.db import models

class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в сети',
        unique=True
    )
    first_name = models.CharField(
        'Имя пользователя',
        blank=True,
        max_length=10
    )
    patronymic = models.CharField(
        'Отчество пользователя',
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
        max_length=20
    )
    passport_date = models.IntegerField(
        'Пасспортные данные',
        blank = True,
        default=0
    )
    birthdate = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    GDPR_status = models.BooleanField(null=True, default=False)
    home_address = models.CharField('Домашний адрес',
                                    max_length=50, blank=True, default='')

    def __str__(self):
        return f'{self.first_name}, {self.external_id}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Stuff(models.Model):
    stuff_name = models.CharField(max_length=256)
    def __str__(self):
        return f'{self.stuff_name}'

    class Meta:
        verbose_name = 'Вещь'
        verbose_name_plural = 'Вещи'


class Stuff_properties(models.Model):
    stuff = models.ForeignKey(Stuff, on_delete=models.CASCADE)
    price_per_week = models.PositiveIntegerField(verbose_name='Цена за неделю')
    price_per_month = models.PositiveIntegerField(verbose_name='Цена за месяц')

    def __str__(self):
        return f'{self.Stuff_properties}'

    class Meta:
        verbose_name = 'Свойства вещи'
        verbose_name_plural = 'Свойства вещей'


class Order(models.Model):
    profile = models.ForeignKey(
        Profile,
        verbose_name='Профиль',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        'Дата создания заказа',
        auto_now_add=True
    )
    order_number = models.PositiveIntegerField('Номер заказа', null=True, default=None, unique=True)
    customer_chat_id = models.CharField(verbose_name='Chat ID Покупателя', null=True, blank=True,
                                        max_length=256)
    order_price = models.PositiveIntegerField(
        verbose_name='Цена заказа', default=0
    )
    comments = models.CharField(verbose_name='Комментарии', null=True, blank=True,
                                max_length=256)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'


class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        on_delete=models.CASCADE
    )
    cell_volume = models.PositiveIntegerField(verbose_name='Объем ячейки')
    storage_address = models.CharField(verbose_name='Адрес ячейки', null=True, blank=True,
                                       max_length=256)
    start_date = models.DateField('Дата начала аренды')
    end_date = models.DateField('Дата окончания аренды')
    Available = 'Ячейка доступна'
    Unavailable = 'Ячейка недоступна'
    order_statuses = [
        (Available, 'Ячейка доступна'),
        (Unavailable, 'Ячейка недоступна')
    ]
    order_status = models.CharField(verbose_name='Статус заказа',
                                    max_length=256,
                                    choices=order_statuses,
                                    default=Available
                                    )
    qr_code = models.ImageField(upload_to='static/qr', height_field=None, width_field=None, max_length=100)

