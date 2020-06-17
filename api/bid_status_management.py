from api.models import BidStatus, Product, Bid

BID_STATUS_MESSAGES = {
    BidStatus.SELLER_SEND: "Seller have dispatched the item to Payouttt warehhouse",
    BidStatus.PAYOUT_RECEIVED: "Payouttt received the items from seller",
    BidStatus.PAYOUT_SEND: "Payouttt send the item to buyer",
}


class BidStatusManagement(object):
    def create_bid_status(self, bid, status):
        if not BidStatus.objects.filter(bid=bid, status=status):
            return BidStatus.objects.create(bid=bid, status=status, status_message=BID_STATUS_MESSAGES.get(status))
        return None

    def get_bid_status(self, bid):
        return BidStatus.objects.filter(bid=bid).order_by('-created_at')

    def add_product_in_bid(self, bid):
        product = Product.objects.filter(sku_number=bid.sku_number, on_hold=False, sold=False,
                                         seller__is_superuser=False,
                                         listing_price__lte=bid.bid_amount, shoe_sizes=bid.shoe_size).order_by(
            'id').first()
        if product:
            product.on_hold = True
            product.save()
            bid.product_to_bid_on = product
            bid.save()

    def link_bid_with_product(self, product):
        bid = Bid.objects.filter(sku_number=product.sku_number, product_to_bid_on__isnull=True,
                                 shoe_size=product.shoe_sizes.all().first()).order_by('id').first()
        if bid:
            bid.product_to_bid_on = product
            product.on_hold = True
            product.save()
            bid.save()
