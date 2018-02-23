from saleor.product.models import ProductVariant, Product


def get_items(checkout):
    product_ids = ProductVariant.objects.filter(id__in=checkout.cart.lines.values('variant')).values('product')
    products = Product.objects.filter(id__in=product_ids)
    items = []
    for product in products:
        items.append(product.to_dict())
    return items
