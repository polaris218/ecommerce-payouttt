from api.models import BidStatus, Product, Bid

BID_STATUS_MESSAGES = {
    BidStatus.SELLER_SEND: "Seller have dispatched the item to QuickKicks warehhouse",
    BidStatus.PAYOUT_RECEIVED: "QuickKicks received the items from seller",
    BidStatus.PAYOUT_SEND: "QuickKicks send the item to buyer",
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
        if product and (product.seller != bid.user):
            product.on_hold = True
            product.save()
            bid.product_to_bid_on = product
            bid.save()

    def link_bid_with_product(self, product):
        bid = Bid.objects.filter(sku_number=product.sku_number, product_to_bid_on__isnull=True,
                                 shoe_size=product.shoe_sizes.all().first()).order_by('id').first()
        if bid and (product.seller != bid.user):
            bid.product_to_bid_on = product
            product.on_hold = True
            product.save()
            bid.save()

    def get_lowest_highest_bid(self, sku_number):
        bids = Bid.objects.filter(sku_number=sku_number).order_by('-bid_amount')
        data = []
        if bids.first():
            data.append(bids.first().bid_amount)
        else:
            data.append(0)
        if bids.last() and bids.last() not in data:
            data.append(bids.last().bid_amount)
        else:
            data.append(0)
        return data

    def get_lowest_highest_listing_price(self, sku_number):
        products = Product.objects.filter(sku_number=sku_number, ).order_by('-listing_price')
        data = []
        if products.first():
            data.append(products.first().listing_price)
        else:
            data.append(0)
        if products.last() and products.last() not in data:
            data.append(products.last().listing_price)
        else:
            data.append(0)
        return data
