import re
import json
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from rest_framework import status

from accounts.STRIPE_payments import StripePayment
from accounts.models import User
from addresses.address_validation import ShippoAddressManagement
from addresses.models import Address
from api.bid_status_management import BidStatusManagement
from api.models import Product, Bid, CartModel
from core.models import FeedbackModel
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

    def verify_payment_method(self, payment_method):
        try:
            return eval(payment_method).get('paymentMethod').get('id')
        except:
            return False

    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.user)
        address_form = MyAddressForm()
        address = Address.objects.filter(user=self.request.user).first()
        if address:
            address_form = MyAddressForm(instance=address)
        secret_key = StripePayment().get_customer_secret(self.request.user)
        strip_publish_key = settings.STRIPE_PUBLISHABLE_KEY
        is_payment_method_added = self.verify_payment_method(request.user.stripe_payment_method)
        return render(request, self.template_name,
                      {'form': form, 'active_password_profile': 'active-tab',
                       'active_dashboard': 'active', 'address_form': address_form, 'secret_key': secret_key,
                       'strip_publish_key': strip_publish_key, 'is_payment_method_added': is_payment_method_added})


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

    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(seller=self.request.user)
        prices = {}
        all_prices = []
        for product in products:
            prices['highest'], prices['lowest'] = BidStatusManagement().get_lowest_highest_bid(product.sku_number)
            all_prices.append(prices)
            prices = {}
        return render(request, self.template_name, {'products': zip(products, all_prices)})


class BuyingView(LoginRequiredMixin, TemplateView):
    template_name = 'admin-buying.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['buying'] = 'active'
        return kwargs

    def get(self, request, *args, **kwargs):
        prices = {}
        all_prices = []
        all_bids = Bid.objects.filter(user=self.request.user, paid=False)
        for bid in all_bids:
            prices['highest'], prices['lowest'] = BidStatusManagement().get_lowest_highest_bid(bid.sku_number)
            all_prices.append(prices)
            prices = {}
        return render(request, self.template_name, {'bids': zip(all_bids, all_prices)})


class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'orders.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['orders'] = 'active'
        return kwargs

    def get(self, request, *args, **kwargs):
        orders = CartModel.objects.filter(user=self.request.user).order_by('-id')
        prices = [(cart.cart_item.all().aggregate(Sum('product__listing_price')))['product__listing_price__sum'] for
                  cart in orders]
        return render(request, self.template_name, {'orders': zip(orders, prices)})


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


class PaymentMethodAddSuccess(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        payment_method = json.loads(request.body)
        user = self.request.user
        if payment_method:
            if user.stripe_customer_id and payment_method.get('paymentMethod').get('id'):
                user.stripe_payment_method = payment_method
                user.save()
                StripePayment().link_paymentmethod_with_customer(user)
        return render(request, 'setting.html')


class FeedBack(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        feedback_description = (request.POST.get('rewardNotes'))
        FeedbackModel.objects.create(user=request.user, description=feedback_description, is_active=True)
        return redirect(reverse('home'))
