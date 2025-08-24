# features/steps/load_steps.py
import os
import requests
from behave import given
from service.common.status import HTTP_201_CREATED, HTTP_200_OK

@given("the following products")
def step_impl(context):
    base = os.getenv("BASE_URL", "http://localhost:8080")
    # reset (helper para los labs)
    requests.delete(f"{base}/admin/reset")
    # carga
    rest_endpoint = f"{base}/products"
    for row in context.table:
        payload = {
            "name": row["name"],
            "description": row["description"],
            "price": row["price"],
            "available": row["available"] in ["True", "true", "1", "yes", "Yes"],
            "category": row["category"],
        }
        resp = requests.post(rest_endpoint, json=payload)
        assert resp.status_code == HTTP_201_CREATED
