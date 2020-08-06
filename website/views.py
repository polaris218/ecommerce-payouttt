import operator
from datetime import datetime
from functools import reduce
import math
import shippo
import stripe
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from Payouttt import settings
from Payouttt.constants import BID_SUCCESS_MESSAGE, BID_FAIL, BID_COMPLETE, \
    SELL_FAIL, SELL_SUCCESS_MESSAGE, SELL_COMPLETE, FAIL_MESSAGE
from accounts.models import User
from addresses.address_validation import ShippoAddressManagement
from addresses.models import Address
from api.bid_status_management import BidStatusManagement
from api.models import Product, Bid, ShoeSize, CartModel, CartItem, SuggestProduct
from core import EmailHelper
from core.EmailHelper import Email
from dashboard.forms import LoginForm, WebSignUpForm, ProductSuggestForm


class IndexView(TemplateView):
    template_name = 'web_index.html'

    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(seller__is_staff=True)
        return render(request, self.template_name, {'products': products})


class CategoryDetailsView(TemplateView):
    template_name = 'categories-detail.html'


class SellingView(TemplateView):
    template_name = 'selling.html'


class AppView(TemplateView):
    template_name = 'app.html'


class NewsView(TemplateView):
    template_name = 'news.html'


class SearchView(TemplateView):
    template_name = 'search.html'

    def get(self, request, *args, **kwargs):
        query_dict = {}
        all_colors = []
        query_dict['seller__is_staff'] = True
        if request.GET.get('product_search'):
            query_dict['title__contains'] = request.GET.get('product_search')
        products = Product.objects.filter(**query_dict)
        brands = Product.objects.all().values('brand').distinct()
        brands = [brand['brand'].strip(',') for brand in brands]
        colors = list(Product.objects.all().values('colorway'))
        release_years = Product.objects.all().values('release_date__year').distinct()
        release_years = [year['release_date__year'] for year in release_years]
        [all_colors.append(nested_color.upper()) for color in colors if color and color['colorway'].split('/') for
         nested_color in color['colorway'].split('/') if nested_color.upper() not in all_colors]
        return render(request, self.template_name,
                      {'products': products, 'brands': brands, 'all_colors': all_colors, 'release_year': release_years})

    def post(self, request, *args, **kwargs):
        filter_products = []
        query_dict = {}
        query_dict['seller__is_staff'] = True
        colors = []
        years = []
        if request.POST.get('product_search'):
            query_dict['title__contains'] = request.POST.get('product_search')
        if request.POST.getlist('selected_brands[]'):
            query_dict['brand__in'] = request.POST.getlist('selected_brands[]')
        if request.POST.getlist('selected_colors[]'):
            colors = request.POST.getlist('selected_colors[]')
        if request.POST.getlist('selected_years[]'):
            years = request.POST.getlist('selected_years[]')
        if request.POST.get('popularity') == 'High':
            products = Product.objects.filter(**query_dict).order_by('-listing_price')
        elif request.POST.get('popularity') == 'Low':
            products = Product.objects.filter(**query_dict).order_by('listing_price')
        elif request.POST.get('popularity') == 'A-Z':
            products = Product.objects.filter(**query_dict).order_by('title')
        elif request.POST.get('popularity') == 'Z-A':
            products = Product.objects.filter(**query_dict).order_by('-title')
        else:
            products = Product.objects.filter(**query_dict)
        if colors:
            [filter_products.append(product) for product in products for color in colors if
             product.colorway.upper().__contains__(color.upper()) and product not in filter_products]
            products = filter_products
        if years:
            products = [product for product in products if str(product.release_date.year) in years]
        return render(request, 'search_ajax.html', {'products': products})


class NewsDetailView(TemplateView):
    template_name = 'news-detail.html'


class ProductDetailView(TemplateView):
    template_name = 'product-detail.html'

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = Product.objects.filter(id=product_id, seller__is_staff=True).first()
        highest_ask, lowest_ask = BidStatusManagement().get_lowest_highest_listing_price(product.sku_number)
        highest_bid, lowest_bid = BidStatusManagement().get_lowest_highest_bid(product.sku_number)

        return render(request, self.template_name,
                      {'product': product, 'lowest_ask': lowest_ask, 'highest_bid': highest_bid})


class WebCartView(LoginRequiredMixin, TemplateView):
    template_name = 'cart.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            cart = CartModel.objects.filter(user=self.request.user, is_active=True).first()
            total_price = 0
            if cart and cart.cart_item.all().count():
                total_price = cart.cart_item.all().aggregate(Sum('product__listing_price'))
                total_price = total_price['product__listing_price__sum']
                cart = cart.cart_item.all()
            else:
                return redirect('web-home')
            return render(request, self.template_name, {'cart': cart, 'total_price': total_price})

    def post(self, request, *args, **kwargs):
        shipping_amount = request.POST.get('shipping')
        shipping_amount, shipping_type = shipping_amount.split('-')
        cart = CartModel.objects.filter(user=self.request.user, is_active=True).first()
        cart.shipping_amount = float(shipping_amount)
        cart.shipping_type = shipping_type
        cart.save()
        return redirect('web_cart_checkout')


class WebCartAddView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        valid_address = ShippoAddressManagement().user_valid_address(self.request.user)
        if valid_address:
            cart = CartModel.objects.filter(user=self.request.user, is_active=True).first()
            if not cart:
                cart = CartModel(user=self.request.user)
                cart.save()
            dict = {}
            shoe_size = ShoeSize.objects.get(id=request.POST.get('shoe_size_id'))
            dict['shoe_size'] = shoe_size
            dict['buyer'] = self.request.user
            dict['product'] = Product.objects.get(id=product_id)
            cart_item_obj = CartItem.objects.create(**dict)
            cart.updated_at = datetime.today()
            cart.cart_item.add(cart_item_obj)
            cart.save()
        return redirect('web_cart')


class WebCartItemDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'cart.html'

    def post(self, request, *args, **kwargs):
        cart_item_id = kwargs.get('cart_item_id')
        cart = CartModel.objects.filter(user=self.request.user).first()
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
        if cart and cart.cart_item.all().count():
            return redirect('web_cart')
        else:
            return redirect('web-home')


class WebCartBidView(TemplateView):
    template_name = 'bid.html'

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = Product.objects.filter(id=product_id, seller__is_staff=True).first()
        can_bid = True
        if request.user.is_authenticated:
            bid = Bid.objects.filter(sku_number=product.sku_number, user=self.request.user)
            if bid:
                can_bid = False
        highest_ask, lowest_ask = BidStatusManagement().get_lowest_highest_listing_price(product.sku_number)
        highest_bid, lowest_bid = BidStatusManagement().get_lowest_highest_bid(product.sku_number)
        context = {'product': product, 'can_bid': can_bid, 'lowest_ask': lowest_ask, 'highest_bid': highest_bid}
        if request.user.is_authenticated:
            context['valid_address'] = ShippoAddressManagement().user_valid_address(self.request.user)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            shoe_size_id = request.POST.get('shoe_size_id')
            bid_amount = request.POST.get('bid_amount')
            sku_number = request.POST.get('sku_number')
            shoe_size = ShoeSize.objects.get(id=shoe_size_id)
            bid_success = False
            valid_address = ShippoAddressManagement().user_valid_address(self.request.user)
            context = {}
            context['message'] = FAIL_MESSAGE
            context['bid'] = BID_FAIL

            if valid_address:
                bid = Bid.objects.filter(sku_number=sku_number, user=self.request.user)
                if not bid:
                    obj = Bid.objects.create(sku_number=sku_number, user=self.request.user,
                                             verified_account=self.request.user.verified_account,
                                             shoe_size=shoe_size,
                                             bid_amount=bid_amount)
                    if obj:
                        if not obj.product_to_bid_on:
                            BidStatusManagement().add_product_in_bid(obj)
                            bid_success = True
                            context['message'] = BID_SUCCESS_MESSAGE
                            context['bid'] = BID_COMPLETE

                        try:
                            Email().send_email_to_seller(obj)
                        except:
                            pass
            context['bid_success'] = bid_success

            return JsonResponse(context)


class WebCartBuyView(TemplateView):
    template_name = 'buy-now.html'

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        can_buy = False
        product = Product.objects.get(id=product_id)
        highest_ask, lowest_ask = BidStatusManagement().get_lowest_highest_listing_price(product.sku_number)
        highest_bid, lowest_bid = BidStatusManagement().get_lowest_highest_bid(product.sku_number)
        context = {'product': product, 'lowest_ask': lowest_ask, 'highest_bid': highest_bid}
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            context['valid_address'] = ShippoAddressManagement().user_valid_address(self.request.user)
            cart_item_obj = CartItem.objects.filter(buyer=self.request.user, product=product)
            if not cart_item_obj:
                can_buy = True
        context['can_buy'] = can_buy
        return render(request, self.template_name, context)


class WebCartSellView(TemplateView):
    template_name = 'sell-now.html'

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        highest_ask, lowest_ask = BidStatusManagement().get_lowest_highest_listing_price(product.sku_number)
        highest_bid, lowest_bid = BidStatusManagement().get_lowest_highest_bid(product.sku_number)
        context = {'product': product, 'highest_bid': highest_bid, 'lowest_ask': lowest_ask}
        product_suggest_form = ProductSuggestForm(request.POST or None)
        context['product_suggest_form'] = product_suggest_form
        if request.user.is_authenticated:
            context['valid_address'] = ShippoAddressManagement().user_valid_address(self.request.user)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            shoe_size_id = request.POST.get('shoe_size_id')
            asking_price = request.POST.get('asking_price')
            product_id = kwargs.get('product_id')
            sku_number = request.POST.get('sku_number')
            sell_success = False
            valid_address = ShippoAddressManagement().user_valid_address(self.request.user)
            context = {}
            context['message'] = FAIL_MESSAGE
            context['bid'] = SELL_FAIL
            if valid_address:
                original_product = Product.objects.get(id=product_id)
                if original_product:
                    sell_product = Product.objects.get(pk=original_product.pk)
                    sell_product.pk = None
                    sell_product.seller = self.request.user
                    sell_product.listing_price = asking_price
                    sell_product.save()
                    shoe_sizes = ShoeSize.objects.filter(id=shoe_size_id)
                    for shoe in shoe_sizes:
                        if shoe not in sell_product.shoe_sizes.all():
                            sell_product.shoe_sizes.add(shoe)
                    BidStatusManagement().link_bid_with_product(sell_product)
                    try:
                        Email().send_product_email_to_seller(sell_product)
                    except:
                        pass
                    sell_success = True
                    context['message'] = SELL_SUCCESS_MESSAGE
                    context['bid'] = SELL_COMPLETE

            context['bid_success'] = sell_success

            return JsonResponse(context)


class WebProductSuggestView(TemplateView):
    template_name = 'sell-now.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            valid_address = ShippoAddressManagement().user_valid_address(self.request.user)
            product_id = request.POST.get('product-id')
            if valid_address:
                form = ProductSuggestForm(request.POST or None)
                if form.is_valid():
                    form = form.save(commit=False)
                    form.user = self.request.user
                    form.save()
            return redirect(reverse('web_cart_sell', args=[product_id]))


class WebCartConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'confirmation.html'

    def get(self, request, *args, **kwargs):
        address = Address.objects.filter(user=self.request.user).first()
        cart = CartModel.objects.filter(user=self.request.user, is_active=True).first()
        total_price = 0
        if cart and cart.cart_item.all().count():
            total_price = cart.cart_item.all().aggregate(Sum('product__listing_price'))
            total_price = total_price['product__listing_price__sum']
            grand_total = math.ceil((total_price + cart.shipping_amount) * 100)
            stripe_key = settings.STRIPE_PUBLISHABLE_KEY
            return render(request, self.template_name, {'address': address, 'cart': cart, 'total_price': total_price,
                                                        'grand_total': grand_total, 'stripe_key': stripe_key})
        else:
            return redirect('web-home')


class WebCartThankYouView(TemplateView):
    template_name = 'thank-you.html'

    def get(self, request, *args, **kwargs):
        cart = CartModel.objects.filter(is_active=False, paid=True).last()
        return render(request, self.template_name, {'cart': cart})


def login_view(request):
    form = LoginForm(request.POST or None)
    signup_form = WebSignUpForm(request.POST or None)
    msg = None
    if request.user.is_authenticated:
        return redirect(reverse('web-profile'))
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect(reverse('web-profile'))
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(reverse('web-profile'))

            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "sign-in-up.html", {"form": form, "msg": msg, "signup_form": signup_form})


def signup_view(request):
    form = LoginForm(request.POST or None)
    signup_form = WebSignUpForm(request.POST or None)
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = WebSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.full_name = user.first_name + " " + user.last_name
            user.save()
            try:
                EmailHelper.Email().send_welcome_email(user)
            except:
                pass
            return redirect(reverse('login'))
    else:
        signup_form = WebSignUpForm()
    return render(request, "sign-in-up.html", {"form": form, "signup_form": signup_form, 'active_form': True})


def logout_view(request):
    logout(request)
    return redirect(reverse('home'))


def stripe_payment_charge(request):  # new
    if request.method == 'POST' and request.user.is_authenticated:
        admin_address = Address.objects.filter(admin_address=True).first()
        seller_address = ShippoAddressManagement().user_valid_address(admin_address.user)
        buyer_address = ShippoAddressManagement().user_valid_address(request.user)
        if seller_address and buyer_address:
            user = User.objects.get(id=request.user.id)
            if user.stripe_customer_id and verify_payment_method(user.stripe_payment_method):
                cart = CartModel.objects.filter(user=request.user, is_active=True).first()
                total_price = 0
                if cart:
                    total_price = cart.cart_item.all().aggregate(Sum('product__listing_price'))
                    total_price = total_price['product__listing_price__sum']
                grand_total = math.ceil((total_price + cart.shipping_amount) * 100)
                try:
                    charge = stripe.Charge.create(
                        amount=grand_total,
                        currency='usd',
                        description='Payouttt charge',
                        source=request.POST['stripeToken']
                    )
                except:
                    return redirect('web_cart_failed')
                if charge['status'] == "succeeded" and charge['paid'] == True:
                    set_user_tracking(user, cart)
                    cart.transaction_id = charge['id']
                    cart.is_active = False
                    cart.paid = True
                    cart.status = CartModel.PAID
                    cart.save()
                    return redirect('web_cart_thank_you')
                else:
                    return redirect('web_cart_failed')
        else:
            msg = 'User must have address added and validated.'
            return render(request, "failed.html", {"msg": msg, })
    else:
        return redirect('web-home')


class WebCartFailedView(TemplateView):
    template_name = 'failed.html'


class WebCartCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        address = Address.objects.filter(user=self.request.user).first()
        cart = CartModel.objects.filter(user=self.request.user, is_active=True).first()
        total_price = 0
        if cart and cart.cart_item.all().count():
            total_price = cart.cart_item.all().aggregate(Sum('product__listing_price'))
            total_price = total_price['product__listing_price__sum']
            grand_total = total_price + cart.shipping_amount
            return render(request, self.template_name, {'address': address, 'cart': cart, 'total_price': total_price,
                                                        'grand_total': grand_total})
        else:
            return redirect('web-home')


def verify_payment_method(payment_method):
    try:
        return eval(payment_method).get('paymentMethod').get('id')
    except:
        return False


def set_user_tracking(user, cart):
    success = True
    try:
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
            address_from=get_admin_address(),
            address_to=buyer_addr,
            parcels=[get_parcel()],
            asynchronous=False
        )
        rate = shipment.rates[0]
        transaction = shippo.Transaction.create(
            rate=rate.object_id, asynchronous=False)
        if transaction.status == "SUCCESS":
            cart.tracking_number = transaction.tracking_number
            cart.tracking_url = transaction.label_url
        else:
            cart.shippo_error = transaction.messages[0].get('text')
            success = False
    except Exception as e:
        cart.shippo_error = str(e)
        success = False
    cart.save()
    return success


def get_admin_address():
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


def get_parcel():
    parcel = {
        "length": "14",
        "width": "10",
        "height": "6",
        "distance_unit": "in",
        "weight": "3",
        "mass_unit": "lb",
    }
    return parcel
