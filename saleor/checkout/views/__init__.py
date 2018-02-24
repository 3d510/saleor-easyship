from django.shortcuts import redirect
from django.template.response import TemplateResponse

from saleor.checkout.views.utils import shipping_info
from saleor.easyship.api import post
from saleor.product.models import Product
from saleor.shipping.models import ShippingMethod, Shipment
from .discount import add_voucher_form, validate_voucher
from .shipping import (anonymous_user_shipping_address_view,
                       user_shipping_address_view)
from .summary import (
    summary_with_shipping_view, anonymous_summary_without_shipping,
    summary_without_shipping)
from .validators import (
    validate_cart, validate_shipping_address,
    validate_shipping_method, validate_is_shipping_required)
from ..core import load_checkout
from ..forms import ShippingMethodForm
from ...account.forms import LoginForm

import json

@load_checkout
@validate_cart
@validate_is_shipping_required
def index_view(request, checkout):
    """Redirect to the initial step of checkout."""
    return redirect('checkout:shipping-address')


@load_checkout
@validate_voucher
@validate_cart
@validate_is_shipping_required
@add_voucher_form
def shipping_address_view(request, checkout):
    """Display the correct shipping address step."""
    if request.user.is_authenticated:
        return user_shipping_address_view(request, checkout)
    return anonymous_user_shipping_address_view(request, checkout)


@load_checkout
@validate_voucher
@validate_cart
@validate_is_shipping_required
@validate_shipping_address
@add_voucher_form
def shipping_method_view(request, checkout):
    """Display the shipping method selection step."""
    # print(checkout.__dict__)
    country_code = checkout.shipping_address.country.code
    shipping_method_country_ids = checkout.storage['shipping_method_country_ids']
    related_products = checkout.storage.get('related_products', [])

    related_product_objs = [(item[0], Product.objects.get(pk=item[1])) for item in related_products]
    print(related_product_objs)

    shipping_method_form = ShippingMethodForm(
        country_code, request.POST or None,
        initial={'method': checkout.shipping_method}
        , shipping_method_country_ids=shipping_method_country_ids
    )
    if shipping_method_form.is_valid():
        checkout.shipping_method = shipping_method_form.cleaned_data['method']
        selected_courier = shipping_method_form.cleaned_data['method']
        # selected_courier_id = ShippingMethod.objects.get(name=selected_courier_name).courier_id
        ship_info = shipping_info(checkout)
        ship_info['selected_courier_id'] = selected_courier.shipping_method.courier_id

        import json
        print(json.dumps(ship_info, indent=True))

        shipment = post("shipment/v1/shipments", ship_info)['shipment']
        print(shipment, request.user)
        # Shipment.objects.create(
        #     easyship_shipment_id=shipment['easyship_shipment_id'],
        #     platform_order_number=shipment['platform_order_number'],
        #     min_delivery_time=shipment['selected_courier']['min_delivery_time'],
        #     max_delivery_time=shipment['selected_courier']['max_delivery_time'],
        #     user=request.user
        # )

        checkout.storage['easyship_shipment_id'] = shipment['easyship_shipment_id']
        checkout.storage['platform_order_number'] = shipment['platform_order_number']
        checkout.storage['min_delivery_time'] = shipment['selected_courier']['min_delivery_time']
        checkout.storage['max_delivery_time'] = shipment['selected_courier']['max_delivery_time']

        return redirect('checkout:summary')
    return TemplateResponse(
        request, 'checkout/shipping_method.html',
        context={
            'shipping_method_form': shipping_method_form,
            'checkout': checkout,
            'related_product_objs': related_product_objs
        })


@load_checkout
@validate_voucher
@validate_cart
@add_voucher_form
def summary_view(request, checkout):
    """Display the correct order summary."""
    if checkout.is_shipping_required:
        view = validate_shipping_address(summary_with_shipping_view)
        view = validate_shipping_method(view)
        return view(request, checkout)
    if request.user.is_authenticated:
        return summary_without_shipping(request, checkout)
    return anonymous_summary_without_shipping(request, checkout)


@load_checkout
@validate_cart
def login(request, checkout):
    """Allow the user to log in prior to checkout."""
    if request.user.is_authenticated:
        return redirect('checkout:index')
    form = LoginForm()
    return TemplateResponse(request, 'checkout/login.html', {'form': form})
