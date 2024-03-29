from django import template
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Payouttt.decorators import staff_required
from accounts.STRIPE_payments import StripePayment
from accounts.models import User
from addresses.address_validation import ShippoAddressManagement
from addresses.models import Address
from api.models import SuggestProduct, CartModel, Bid
from core.models import FeedbackModel, AdminTransaction
from dashboard.forms import LoginForm, SignUpForm, AddressForm
from dashboard.services import BidManagement


@method_decorator(staff_required, name='dispatch')
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        kwargs['paid_bids'] = BidManagement().get_paid_bids()
        # kwargs['non_paid_bids'] = BidManagement().get_non_paid_bids()
        kwargs['daily'] = BidManagement().get_daily_sales()
        kwargs['monthly'] = BidManagement().get_monthly_sales()
        kwargs['yearly'] = BidManagement().get_yearly_sales()
        kwargs['dashboard'] = 'active'
        return kwargs


@method_decorator(staff_required, name='dispatch')
class NonPaidOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'non_paid_orders.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        kwargs['paid_bids'] = BidManagement().get_non_paid_bids()
        kwargs['orders'] = 'active'
        return kwargs


@method_decorator(staff_required, name='dispatch')
class AllOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'admin-orders.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        kwargs['all_orders'] = 'active'
        return kwargs

    def get(self, request, *args, **kwargs):
        orders = CartModel.objects.all().order_by('-id')
        prices = [(cart.cart_item.all().aggregate(Sum('product__listing_price')))['product__listing_price__sum'] for
                  cart in orders]
        return render(request, self.template_name, {'orders': zip(orders, prices)})


@method_decorator(staff_required, name='dispatch')
class AllPaidOrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'paid_orders.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        get_paid_bids = BidManagement().get_paid_bids()
        admin_paid_bids = []
        admin_unpaid_bids = []
        [admin_paid_bids.append(bid) if AdminTransaction.objects.filter(bid=bid, paid=True).first()
         else admin_unpaid_bids.append(bid) for bid in get_paid_bids]
        kwargs['admin_unpaid_bids'] = admin_unpaid_bids
        kwargs['admin_paid_bids'] = admin_paid_bids
        kwargs['paid_orders'] = 'active'
        return kwargs


@method_decorator(staff_required, name='dispatch')
class OrderDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'non_paid_orders.html'

    def post(self, request, *args, **kwargs):
        id = kwargs.get('id')
        BidManagement().remove_bid(id)
        return redirect(reverse('non_paid_orders'))


# @method_decorator(staff_required, name='dispatch')
class AddressView(LoginRequiredMixin, TemplateView):
    template_name = 'address.html'

    def get_object(self):
        return Address.objects.filter(user=self.request.user).first()

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        kwargs['address'] = 'active'
        form = AddressForm()
        address = self.get_object()
        if address:
            form = AddressForm(instance=address)
        kwargs['form'] = form
        return kwargs

    def post(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)
        address = self.get_object()
        request_data = request.POST.copy()
        request_data['user'] = self.request.user.id
        request_data['email'] = self.request.user.email
        request_data['validate'] = self.request.user.email
        form = AddressForm(request_data)
        if address:
            form = AddressForm(request_data, instance=address)
        if form.is_valid():
            valid_address, message, address_id = ShippoAddressManagement().validate_address(request_data)
            if valid_address:
                address = form.save()
                address.shippo_address_id = address_id
                address.is_valid = True
                address.admin_address = True
                address.save()
                return redirect(reverse('address'))
            else:
                context['form'] = form
                context['message'] = message
                return self.render_to_response(context)
        context['form'] = form
        return self.render_to_response(context)


@method_decorator(staff_required, name='dispatch')
class ProductSuggestionsView(LoginRequiredMixin, TemplateView):
    template_name = 'suggestions_products.html'

    def get(self, request, *args, **kwargs):
        suggestions = SuggestProduct.objects.all().order_by('-id')
        return render(request, self.template_name, {'suggestions': suggestions})


@method_decorator(staff_required, name='dispatch')
class DashboardFeedback(LoginRequiredMixin, TemplateView):
    template_name = 'feedbacks.html'

    def get(self, request, *args, **kwargs):
        feedbacks = FeedbackModel.objects.filter(is_active=True).order_by('-id')
        return render(request, self.template_name, {'feedbacks': feedbacks})


@method_decorator(staff_required, name='dispatch')
class TypoView(LoginRequiredMixin, TemplateView):
    template_name = 'ui-icons.html'


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


@method_decorator(staff_required, name='dispatch')
class TransferFundsView(LoginRequiredMixin, TemplateView):
    template_name = 'feedbacks.html'

    def post(self, request, *args, **kwargs):
        bid = Bid.objects.filter(id=request.POST.get('bid_id')).first()
        user = User.objects.filter(id=bid.product_to_bid_on.seller.id).first()
        transaction = AdminTransaction.objects.filter(user__id=user.id).first()
        StripePayment().transfer_amount(transaction, bid)
        return redirect('all_paid_orders')
