from django.contrib.auth.forms import PasswordChangeForm
from django import forms

from addresses.models import Address
from localflavor.us.us_states import STATE_CHOICES


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': "Old Password"})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': "New Password"})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': "New Password"})

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class MyAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('created_at', 'updated_at', 'is_valid', 'shippo_address_id', 'admin_address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({'class': 'form-control', 'placeholder': "Full Name"})
        self.fields['company'].widget.attrs.update({'class': 'form-control', 'placeholder': "Company"})
        self.fields['street1'].widget.attrs.update({'class': 'form-control', 'placeholder': "Street Address"})
        self.fields['city'].widget.attrs.update({'class': 'form-control', 'placeholder': "City"})

        self.fields['state'].widget.attrs.update({'class': 'form-control', 'placeholder': "State"})

        self.fields['zip'].widget.attrs.update({'class': 'form-control', 'placeholder': "Zip"})
        self.fields['country'].widget.attrs.update({'class': 'form-control', 'placeholder': "Country"})
        # self.fields['state'].widget = forms.TextInput()
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['company'].initial = 'Payouttt'
        self.fields['company'].widget = forms.HiddenInput()
