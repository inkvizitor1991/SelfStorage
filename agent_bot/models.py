from django.db import models

class Profile(models.Model):
    full_name = models.CharField(
        'ФИО пользователя',
        null=True,
        blank=True,
        max_length=256
    )
    tg_chat_id = models.CharField(verbose_name='Chat ID Покупателя', null=True, blank=True,
                                        max_length=256)
    phone = models.CharField(
        'Телефон пользователя',
        blank=True,
        max_length=20,
        default='+'
    )
    passport_date = models.CharField(
        'Пасспортные данные',
        null=True, blank=True,
        max_length=256
    )
    birthdate = models.CharField(verbose_name='Дата рождения', null=True, blank=True, max_length=50)

    def __str__(self):
        return f'{self.full_name}'

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
    order_price = models.PositiveIntegerField(
        verbose_name='Цена заказа', default=0
    )
    things = models.CharField(verbose_name='Вещи для храннения', max_length=256, default='')
    storage_address = models.CharField(verbose_name='Адрес ячейки', null=True, blank=True,
                                       max_length=256, default='')
    start_date = models.DateTimeField('Дата начала аренды', auto_now_add=True)
    end_date = models.DateTimeField('Дата окончания аренды', auto_now_add=True)
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
    qr_code = models.ImageField(upload_to='static/qr', height_field=None, width_field=None, max_length=100, default=None)
    comments = models.CharField(verbose_name='Комментарии', null=True, blank=True,
                                max_length=256, default='')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'


class Promo_code():
    month = models.CharField(verbose_name='Месяц действия промокода', null=True, blank=True,
                                       max_length=256)
    promo_code = models.CharField(verbose_name='Промокод', null=True, blank=True,
                                       max_length=256)
    percent_discount = models.IntegerField(verbose_name='Процент скидки', null=True, blank=True)
