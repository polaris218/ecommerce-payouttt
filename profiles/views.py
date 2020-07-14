import re

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse

from accounts.models import User
from addresses.address_validation import ShippoAddressManagement
from addresses.models import Address
from dashboard.views import AddressView
from profiles.forms import MyPasswordChangeForm, MyAddressForm


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    form_class = MyPasswordChangeForm

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['profile'] = 'active'
        return kwargs

    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.user)
        address_form = MyAddressForm()
        address = Address.objects.filter(user=self.request.user).first()
        if address:
            address_form = MyAddressForm(instance=address)
        return render(request, self.template_name,
                      {'form': form, 'active_password_profile': 'active-tab',
                       'active_dashboard': 'active', 'address_form': address_form})


class SecurityView(LoginRequiredMixin, TemplateView):
    template_name = 'security.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['security'] = 'active'
        return kwargs


class SellingView(LoginRequiredMixin, TemplateView):
    template_name = 'web-admin-selling.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['selling'] = 'active'
        return kwargs


class BuyingView(LoginRequiredMixin, TemplateView):
    template_name = 'admin-buying.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['buying'] = 'active'
        return kwargs


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['dashboard'] = 'active'
        return kwargs


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'setting.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['settings'] = 'active'
        return kwargs


class PasswordResetView(LoginRequiredMixin, TemplateView):
    form_class = MyPasswordChangeForm
    template_name = 'password_change_ajax.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return render(request, self.template_name, {'form': form, 'password_changed': True})
        else:
            return render(request, self.template_name, {'form': form, 'password_changed': False})


class ChangeUserName(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        new_full_name = request.POST.get('new_name')
        user = User.objects.get(id=request.user.id)
        if new_full_name:
            user.full_name = new_full_name
        else:
            user.full_name = user.first_name + " " + user.last_name
        user.save()
        return render(request, 'setting.html')


class ChangeReturnAddress(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        return_address = request.POST.get('address')
        user = User.objects.get(id=request.user.id)
        user.return_address = return_address
        user.save()
        return render(request, 'setting.html')


class UserAddressView(AddressView, TemplateView):
    template_name = 'address_form_ajax.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        kwargs['address'] = 'active'
        form = MyAddressForm()
        address = self.get_object()
        if address:
            form = MyAddressForm(instance=address)
        kwargs['address_form'] = form
        self.template_name = 'address_form_ajax.html'
        return kwargs

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        address = self.get_object()
        request_data = request.POST.copy()
        request_data['user'] = self.request.user.id
        request_data['email'] = self.request.user.email
        request_data['validate'] = self.request.user.email
        form = MyAddressForm(request_data)
        if address:
            form = MyAddressForm(request_data, instance=address)
        if form.is_valid():
            valid_address, message, address_id = ShippoAddressManagement().validate_address(request_data)
            if valid_address:
                address = form.save()
                address.shippo_address_id = address_id
                address.is_valid = True
                address.admin_address = False
                address.save()
                context['address_form'] = MyAddressForm(instance=address)
                context['message'] = "Successfully Updated."
                return self.render_to_response(context)
            else:
                context['form'] = form
                context['message'] = message
                return self.render_to_response(context)
        context['address_form'] = form
        return self.render_to_response(context)
