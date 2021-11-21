from django.contrib import admin
from .models import Order, Profile, Stuff, Stuff_categories, Stuff


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['full_name']
    list_display = (
        'id', 'tg_chat_id', 'full_name', 'phone', 'passport_date', 'birthdate'
    )


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile',
                    'created_at', 'order_number',
                    'order_price', 'things',
                    'storage_address', 'order_status', #'start_date', 'end_date',
                    'qr_code', 'comments'
                    )


class Stuff_categoriesAdmin(admin.ModelAdmin):
    search_fields = ['categories_name']


class StuffAdmin(admin.ModelAdmin):
    list_display = ('stuff_categories', 'stuff_name', 'price_per_week', 'price_per_month')


class Promo_codeAdmin(admin.ModelAdmin):
    list_display = ('month', 'promo_code', 'percent_discount')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Stuff, StuffAdmin)
admin.site.register(Stuff_categories, Stuff_categoriesAdmin)
