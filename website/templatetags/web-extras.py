from django import template
from api.models import Product

register = template.Library()


@register.simple_tag
def get_product_sku_sizes_list_tag(sku_number):
    sku = sku_number
    filter_products = []
    ids = []
    all_sizes = []
    sku_products = Product.objects.filter(sku_number=sku).values('shoe_sizes', 'shoe_sizes__country',
                                                                 'shoe_sizes__shoe_size',
                                                                 'shoe_sizes__product__listing_price').distinct().order_by(
        'shoe_sizes')
    for pro in sku_products:
        if pro['shoe_sizes'] not in ids:
            ids.append(pro['shoe_sizes'])
    for ide in (ids):
        price = Product.objects.filter(shoe_sizes__in=[ide], sku_number=sku).order_by(
            'listing_price').values('shoe_sizes', 'shoe_sizes__country',
                                    'shoe_sizes__shoe_size',
                                    'shoe_sizes__product__listing_price')
        filter_products.append(price.first())
    for product in sku_products:
        for nest_product in sku_products:
            if nest_product['shoe_sizes__country'] == product['shoe_sizes__country']:
                if nest_product['shoe_sizes__shoe_size'] == product['shoe_sizes__shoe_size']:
                    if nest_product['shoe_sizes__product__listing_price'] < product[
                        'shoe_sizes__product__listing_price']:
                        for pro in filter_products:
                            if pro['shoe_sizes__country'] == nest_product['shoe_sizes__country']:
                                if pro['shoe_sizes__shoe_size'] == nest_product['shoe_sizes__shoe_size']:
                                    if pro['shoe_sizes__product__listing_price'] > nest_product[
                                        'shoe_sizes__product__listing_price']:
                                        pro['shoe_sizes__product__listing_price'] = nest_product[
                                            'shoe_sizes__product__listing_price']

    for size in filter_products:
        all_sizes.append({'id': size['shoe_sizes'],
                          'name': (str(size['shoe_sizes__country']) + "-" + str(size['shoe_sizes__shoe_size'])),
                          "price": size['shoe_sizes__product__listing_price']})
    return all_sizes
