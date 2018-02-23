from saleor.product.models import ProductVariant


def get_items(checkout):
    products = ProductVariant.objects.filter(id__in=checkout.cart.lines.values('variant')).values('product')
    items = []
    for product in products:
        items.append(product.to_dict())
    return items
