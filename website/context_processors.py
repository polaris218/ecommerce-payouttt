from api.models import CartModel


def cart_info(request):
    cart = CartModel.objects.filter(user=request.user, is_active=True).first()
    total_cart_items = 0
    if cart:
        total_cart_items = cart.cart_item.all().count()
    return {"total_cart_items": total_cart_items}
