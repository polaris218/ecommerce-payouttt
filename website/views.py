from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from core import EmailHelper
from dashboard.forms import LoginForm, WebSignUpForm


class IndexView(TemplateView):
    template_name = 'web_index.html'


class CategoryDetailsView(TemplateView):
    template_name = 'categories-detail.html'


class SellingView(TemplateView):
    template_name = 'selling.html'


class AppView(TemplateView):
    template_name = 'app.html'


class NewsView(TemplateView):
    template_name = 'news.html'


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
