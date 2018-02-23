import requests
import json

HOSTING_URL = "https://api.easyship.com/"
HEADER = {"Content-Type": "application/json", "Authorization": "Bearer prod_7J8bff5sfosdM/5l7Kg5y2Un8qMhQCCKj2idK7OJQz8="}

# def get_token():
#     return "prod_7J8bff5sfosdM/5l7Kg5y2Un8qMhQCCKj2idK7OJQz8="


def get(endpoint):
    r = requests.get(HOSTING_URL + endpoint, headers = HEADER)
    return json.loads(r.text)

def post(endpoint, data):
    r = requests.post(HOSTING_URL + endpoint, data=json.dumps(data), headers=HEADER)
    return json.loads(r.text)

## example
print(get("reference/v1/categories"))
print(post("rate/v1/rates", data={
    "origin_country_alpha2": "SG",
    "origin_postal_code": "059405",
    "destination_country_alpha2": "US",
    "destination_postal_code": 10030,
    "taxes_duties_paid_by": "Sender",
    "is_insured": False,
    "items": [
        {
            "actual_weight": 1.2,
            "height": 10,
            "width": 15,
            "length": 20,
            "category": "mobiles",
            "declared_currency": "SGD",
            "declared_customs_value": 100
        }
    ]
})["rates"][0]["shipment_charge_total"])
