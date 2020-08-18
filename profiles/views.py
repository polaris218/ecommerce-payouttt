import math
import re
import json
import shippo
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
from accounts.models import User, Plaid
from addresses.address_validation import ShippoAddressManagement
from addresses.models import Address
from api.bid_status_management import BidStatusManagement
from api.models import Product, Bid, CartModel, BidStatus
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
        active_prices = []
        pending_prices = []
        complete_prices = []
        bid_prices = []
        complete_bids = Bid.objects.filter(user=self.request.user, paid=True)
        all_unpaid_bids = Bid.objects.filter(user=self.request.user, paid=False, )
        pending_bids = []
        active_bids = []
        [active_bids.append(bid) if bid.product_to_bid_on else pending_bids.append(bid) for bid in all_unpaid_bids]
        stripe_key = settings.STRIPE_PUBLISHABLE_KEY
        for bid in active_bids:
            prices['highest'], prices['lowest'] = BidStatusManagement().get_lowest_highest_bid(bid.sku_number)
            active_prices.append(prices)
            bid_prices.append(math.ceil((bid.bid_amount + 13) * 100))
            prices = {}
        for bid in pending_bids:
            prices['highest'], prices['lowest'] = BidStatusManagement().get_lowest_highest_bid(bid.sku_number)
            pending_prices.append(prices)
            prices = {}
        for bid in complete_bids:
            prices['highest'], prices['lowest'] = BidStatusManagement().get_lowest_highest_bid(bid.sku_number)
            complete_prices.append(prices)
            prices = {}

        return render(request, self.template_name, {'active_bids': zip(active_bids, active_prices, bid_prices),
                                                    'pending_bids': zip(pending_bids, pending_prices),
                                                    'complete_bids': zip(complete_bids, complete_prices),
                                                    'stripe_key': stripe_key})


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
        prices = [(cart.cart_item.all().aggregate(Sum('price')))['price__sum'] for cart in orders]
        return render(request, self.template_name, {'orders': zip(orders, prices)})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['dashboard'] = 'active'
        return kwargs

    def get(self, request, *args, **kwargs):
        latest_products = Product.objects.filter(seller__is_staff=True).order_by('-id')[:3]
        return render(request, self.template_name, {'latest_products': latest_products})


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


class PayForBidWebView(LoginRequiredMixin, View):

    def get_admin_address(self):
        admin_address = ShippoAddressManagement().get_adming_address()
        admin_addr = {
            "name": admin_address.full_name,
            "street1": admin_address.street1,
            "street2": "",
            "city": admin_address.city,
            "state": admin_address.state,
            "zip": admin_address.zip,
            "country": admin_address.country,
            "phone": "+1 123 456 789",
        }
        return admin_addr

    def get_parcel(self):
        parcel = {
            "length": "14",
            "width": "10",
            "height": "6",
            "distance_unit": "in",
            "weight": "3",
            "mass_unit": "lb",
        }
        return parcel

    def set_user_tracking(self, user, bid_payment, seller=True):

        try:
            if seller:
                address = ShippoAddressManagement().user_valid_address(user)
                seller_addr = {
                    "name": address.full_name or 'Payoutttt',
                    "street1": address.street1,
                    "city": address.city,
                    "state": str(address.state),
                    "zip": int(address.zip),
                    "country": address.country,
                    # "phone": str(user.phone_number),
                }

                shipment = shippo.Shipment.create(
                    address_from=seller_addr,
                    address_to=self.get_admin_address(),
                    parcels=[self.get_parcel()],
                    asynchronous=False
                )
            else:
                address = ShippoAddressManagement().user_valid_address(user)
                buyer_addr = {
                    "name": address.full_name or 'Payoutttt',
                    "street1": address.street1,
                    "city": address.city,
                    "state": str(address.state),
                    "zip": int(address.zip),
                    "country": address.country,
                    # "phone": str(user.phone_number),
                }

                shipment = shippo.Shipment.create(
                    address_from=self.get_admin_address(),
                    address_to=buyer_addr,
                    parcels=[self.get_parcel()],
                    asynchronous=False
                )
            rate = shipment.rates[0]
            transaction = shippo.Transaction.create(
                rate=rate.object_id, asynchronous=False)
            if transaction.status == "SUCCESS":
                if seller:
                    bid_payment.seller_tracking = transaction.tracking_number
                    bid_payment.seller_purchase_label = transaction.label_url
                else:
                    bid_payment.purchase_tracking = transaction.tracking_number
                    bid_payment.purchase_label = transaction.label_url

            else:
                if seller:
                    bid_payment.seller_shippo_error = transaction.messages[0].get('text')
                else:
                    bid_payment.buyer_shippo_error = transaction.messages[0].get('text')
        except Exception as e:
            if seller:
                bid_payment.seller_shippo_error = str(e)
            else:
                bid_payment.buyer_shippo_error = str(e)
        bid_payment.save()

    def get_bid_payment(self, bid):
        return bid.bidpayment_set.all().first()

    def verify_payment_method(self, payment_method):
        try:
            return eval(payment_method).get('paymentMethod').get('id')
        except:
            return False

    def post(self, request, *args, **kwargs):
        bid = Bid.objects.filter(id=kwargs.get('bid_id'), user=self.request.user, paid=False).first()
        if bid:
            seller_address = ShippoAddressManagement().user_valid_address(bid.product_to_bid_on.seller)
            buyer_address = ShippoAddressManagement().user_valid_address(bid.user)
            if seller_address and buyer_address:
                bid_payment = self.get_bid_payment(bid)
                if bid.user.stripe_customer_id and self.verify_payment_method(bid.user.stripe_payment_method):
                    if not bid_payment:
                        bid_payment = StripePayment().bid_payment(bid, request)
                    if bid_payment:
                        self.set_user_tracking(bid.user, bid_payment, seller=False)
                        self.set_user_tracking(bid.product_to_bid_on.seller, bid_payment, seller=True)
                        BidStatusManagement().create_bid_status(bid, BidStatus.SELLER_SEND)
                        return redirect('PayForBidViewSuccess')
                    else:
                        bid.paid = False
                        bid.save()
        return redirect('PayForBidViewFailed')


class BidPaySuccessWeb(View):
    template_name = 'bid_pay_success.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class BidPayFailWeb(View):
    template_name = 'bid_pay_failed.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
