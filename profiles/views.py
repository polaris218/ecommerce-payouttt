from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        kwargs['profile'] = 'active'
        return kwargs


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
