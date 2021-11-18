from django.contrib import admin
from .models import Order, Profile, Stuff, Stuff_categories, Stuff


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = (
        'id', 'external_id', 'first_name', 'last_name', 'phone'

    )


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at')


class Stuff_categoriesAdmin(admin.ModelAdmin):
    search_fields = ['categories_name']

class StuffAdmin(admin.ModelAdmin):
    list_display = ('stuff_categories', 'stuff_name', 'price_per_week', 'price_per_month')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Stuff, StuffAdmin)
admin.site.register(Stuff_categories, Stuff_categoriesAdmin)
