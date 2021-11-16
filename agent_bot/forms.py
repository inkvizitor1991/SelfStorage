from django import forms
from .models import Profile, Order

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'external_id',
            'name',
            'first_name',
            'last_name',
            'phone'

        )
        widgets = {
            'name':forms.TextInput,
            'external_id':forms.TextInput,
            'first_name':forms.TextInput,
            'last_name':forms.TextInput,
            'phone':forms.TextInput

        }
class MessageForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'id',
            'profile',

        )
        widgets = {
            'id':forms.TextInput,
            'profile':forms.TextInput,
        }

