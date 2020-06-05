from api.models import BidStatus

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
