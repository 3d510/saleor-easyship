from django.shortcuts import redirect
from django.template.response import TemplateResponse

from saleor.checkout.views.utils import get_items
from saleor.easyship.api import post
from saleor.shipping.models import ShippingMethod, ShippingMethodCountry
from ...account.forms import get_address_form
from ...account.models import Address
from ..forms import AnonymousUserShippingForm, ShippingAddressesForm


def anonymous_user_shipping_address_view(request, checkout):
    """Display the shipping step for a user who is not logged in."""
    address_form, preview = get_address_form(
        request.POST or None, country_code=request.country.code,
        autocomplete_type='shipping',
        initial={'country': request.country.code},
        instance=checkout.shipping_address)

    user_form = AnonymousUserShippingForm(
        not preview and request.POST or None, initial={'email': checkout.email}
        if not preview else request.POST.dict())
    if all([user_form.is_valid(), address_form.is_valid()]):
        checkout.shipping_address = address_form.instance

        checkout.email = user_form.cleaned_data['email']
        return redirect('checkout:shipping-method')
    return TemplateResponse(
        request, 'checkout/shipping_address.html', context={
            'address_form': address_form, 'user_form': user_form,
            'checkout': checkout})


def user_shipping_address_view(request, checkout):
    """Display the shipping step for a logged in user.

    In addition to entering a new address the user has an option of selecting
    one of the existing entries from their address book.
    """

    data = request.POST or None
    additional_addresses = request.user.addresses.all()
    checkout.email = request.user.email
    shipping_address = checkout.shipping_address

    if shipping_address is not None and shipping_address.id:
        address_form, preview = get_address_form(
            data, country_code=request.country.code,
            initial={'country': request.country})
        addresses_form = ShippingAddressesForm(
            data, additional_addresses=additional_addresses,
            initial={'address': shipping_address.id})
    elif shipping_address:
        address_form, preview = get_address_form(
            data, country_code=shipping_address.country.code,
            instance=shipping_address)
        addresses_form = ShippingAddressesForm(
            data, additional_addresses=additional_addresses)
    else:
        address_form, preview = get_address_form(
            data, initial={'country': request.country},
            country_code=request.country.code)
        addresses_form = ShippingAddressesForm(
            data, additional_addresses=additional_addresses)

    if addresses_form.is_valid() and not preview:
        if (addresses_form.cleaned_data['address'] !=
                ShippingAddressesForm.NEW_ADDRESS):
            address_id = addresses_form.cleaned_data['address']
            checkout.shipping_address = Address.objects.get(id=address_id)
            checkout.storage['shipping_method_country_ids'] = get_couriers(checkout)
            return redirect('checkout:shipping-method')
        elif address_form.is_valid():
            checkout.shipping_address = address_form.instance
            # print(checkout.storage)
            checkout.storage['shipping_method_country_ids'] = get_couriers(checkout)
            # print(checkout.__dict__)
            return redirect('checkout:shipping-method')
    return TemplateResponse(
        request, 'checkout/shipping_address.html', context={
            'address_form': address_form, 'user_form': addresses_form,
            'checkout': checkout,
            'additional_addresses': additional_addresses})


def get_couriers(checkout):
    # return list of shipping_method_country ids

    items = get_items(checkout)
    postal_code = checkout.__dict__['storage']['shipping_address']['postal_code']
    country_code = checkout.__dict__['storage']['shipping_address']['country']
    data = {
        "origin_country_alpha2": "SG",
        "origin_postal_code": "639778",
        "destination_country_alpha2": country_code,
        "destination_postal_code": postal_code,
        "taxes_duties_paid_by": "Sender",
        "is_insured": False,
        "items": items
    }
    rates = post("rate/v1/rates", data).get('rates', [])
    results = []

    for rate in rates:
        # results.append({
        #     "courier_id": rate["courier_id"],
        #     "courier_name": rate["courier_name"],
        #     "charge": rate['shipment_charge_total']
        # })
        shipping_method, created = ShippingMethod.objects.get_or_create(
            name=rate["courier_name"],
            courier_id=rate["courier_id"])
        shipping_method_country, created = ShippingMethodCountry.objects.get_or_create(
            country_code=country_code,
            price=rate['shipment_charge_total'],
            postal_code=postal_code,
            shipping_method=shipping_method
        )
        results.append(shipping_method_country.pk)
    return results
