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
    tg_chat_id = models.CharField(verbose_name='Chat ID Покупателя', null=True, blank=True,
                                        max_length=256)
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
    home_address = models.CharField('Домашний адрес',
                                    max_length=50, blank=True, default='')

    def __str__(self):
        return f'{self.first_name}, {self.external_id}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Stuff_categories(models.Model):
    categories_name = models.CharField(max_length=256)
    def __str__(self):
        return f'{self.categories_name}'

    class Meta:
        verbose_name = 'Категория вещей'
        verbose_name_plural = 'Категорий вещей'


class Stuff(models.Model):
    stuff_categories = models.ForeignKey(Stuff_categories, on_delete=models.CASCADE, default = None)
    stuff_name = models.CharField(verbose_name='Назвние вещи',max_length=256)
    price_per_week = models.PositiveIntegerField(verbose_name='Цена за неделю', default = 100)
    price_per_month = models.PositiveIntegerField(verbose_name='Цена за месяц', default = 100)

    def __str__(self):
        return f'{self.stuff_name}'

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


class Promo_code():
    month = models.CharField(verbose_name='Месяц действия промокода', null=True, blank=True,
                                       max_length=256)
    promo_code = models.CharField(verbose_name='Промокод', null=True, blank=True,
                                       max_length=256)
    percent_discount = models.IntegerField(verbose_name='Процент скидки', null=True, blank=True)
