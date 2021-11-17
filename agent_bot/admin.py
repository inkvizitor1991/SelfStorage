from django.contrib import admin
#from .forms import ProfileForm, MessageForm
from .models import Order, Profile


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = (
        'id', 'external_id', 'first_name', 'last_name', 'phone'

    )
    #form = ProfileForm


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at')
    #form = MessageForm


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Order, OrderAdmin)
