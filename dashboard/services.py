from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from api.models import Bid


class BidManagement(object):
    def remove_bid(self, id):
        Bid.objects.filter(id=id).delete()

    def get_paid_bids(self):
        return Bid.objects.filter(paid=True).order_by('-id')

    def get_non_paid_bids(self):
        return Bid.objects.filter(paid=False).order_by('-id')

    def get_yearly_sales(self):
        yearly = timezone.now() - timedelta(days=12 * 30)
        bids_amount = Bid.objects.filter(paid=True, timestamp__date__gte=yearly.date()).aggregate(
            total=Sum('bid_amount')).get('total')
        return bids_amount or 0

    def get_daily_sales(self):
        bids_amount = Bid.objects.filter(paid=True, timestamp__date=timezone.now().date()).aggregate(
            total=Sum('bid_amount')).get('total')
        return bids_amount or 0

    def get_monthly_sales(self):
        bid_amount = self.get_yearly_sales()
        return round(bid_amount / 12, 2) if bid_amount else 0
