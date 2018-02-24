from django_countries import countries

from saleor.product.models import ProductVariant, Product


PLATFORM_NAME = "TheWatchStrategy"

def get_items(checkout):
    items = []
    # product_ids = ProductVariant.objects.filter(id__in=checkout.cart.lines.values('variant')).values('product')
    print(checkout.cart.lines.__dict__)
    variants = [ProductVariant.objects.get(pk=variant['variant']) for variant in checkout.cart.lines.values('variant')]
    for variant in variants:
        product = variant.product
        items.append(product.to_dict())
    # products = Product.objects.filter(id__in=product_ids)
    # items = []
    # for product in products:
    #     items.append(product.to_dict())
    print("items: ", len(items))
    return items


def shipping_info(checkout):
    city = checkout.__dict__['storage']['shipping_address']['city']
    country_alpha2 = checkout.__dict__['storage']['shipping_address']['country']
    for c in countries:
        if c[0] == country_alpha2:
            country = c[1]
    return {
        "destination_country_alpha2": checkout.__dict__['storage']['shipping_address']['country'],
        "destination_city":  city or country,
        "destination_name":  checkout.__dict__['storage']['shipping_address']['first_name']+checkout.__dict__['storage']['shipping_address']['last_name'] ,
        "destination_address_line_1": checkout.__dict__['storage']['shipping_address']['street_address_1'],
        "destination_phone_number": checkout.__dict__['storage']['shipping_address']['phone'],
        "items": get_items(checkout),
        "platform_name": PLATFORM_NAME,
        "platform_order_number": "#1234",
        "taxes_duties_paid_by": "Sender",
        "is_insured": True,
        "selected_courier_id": "b8d528a7-a2d4-4510-a7ac-11cbbb6542cd",#checkout.shipping_method,
        "destination_postal_code": checkout.__dict__['storage']['shipping_address']['postal_code'],
        "destination_state": checkout.__dict__['storage']['shipping_address']['city'],
        "destination_address_line_2": checkout.__dict__['storage']['shipping_address']['street_address_2'],
        "destination_email_address": checkout.__dict__['storage']['email']
    }


