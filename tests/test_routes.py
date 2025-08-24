# tests/test_routes.py
from service.app import create_app
from service.common import status


def _client():
    app = create_app(testing=True)
    return app.test_client()


def _mk(client, **overrides):
    payload = {
        "name": "Notebook",
        "description": "A5 ruled",
        "price": "9.90",
        "available": True,
        "category": "HOUSEWARES",
    }
    payload.update(overrides)
    resp = client.post("/products", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.get_json()["id"]


# ------------------ HAPPY PATHS ------------------ #
def test_read_product():
    client = _client()
    pid = _mk(client)
    r = client.get(f"/products/{pid}")
    assert r.status_code == status.HTTP_200_OK
    body = r.get_json()
    assert body["id"] == pid
    assert body["name"] == "Notebook"

    # not found
    assert client.get("/products/999999").status_code == \
        status.HTTP_404_NOT_FOUND


def test_update_product():
    client = _client()
    pid = _mk(client)
    r = client.put(
        f"/products/{pid}",
        json={
            "name": "Notebook",
            "description": "Updated",
            "price": "10.50",
            "available": True,
            "category": "HOUSEWARES",
        },
    )
    assert r.status_code == status.HTTP_200_OK
    body = r.get_json()
    assert body["description"] == "Updated"
    assert body["price"] == "10.50"


def test_delete_product():
    client = _client()
    pid = _mk(client)
    r = client.delete(f"/products/{pid}")
    assert r.status_code == status.HTTP_204_NO_CONTENT
    assert r.data == b""

    # idempotente
    r = client.delete(f"/products/{pid}")
    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_list_all_products():
    client = _client()
    _mk(client, name="A")
    _mk(client, name="B")
    r = client.get("/products")
    assert r.status_code == status.HTTP_200_OK
    body = r.get_json()
    assert isinstance(body, list)
    assert len(body) == 2


def test_list_by_name():
    client = _client()
    _mk(client, name="OnlyThis")
    _mk(client, name="Other")
    r = client.get("/products?name=OnlyThis")
    assert r.status_code == status.HTTP_200_OK
    body = r.get_json()
    assert all(p["name"] == "OnlyThis" for p in body)


def test_list_by_category():
    client = _client()
    _mk(client, category="FOOD")
    _mk(client, category="HOUSEWARES")
    r = client.get("/products?category=FOOD")
    assert r.status_code == status.HTTP_200_OK
    body = r.get_json()
    assert all(p["category"] == "FOOD" for p in body)


def test_list_by_availability():
    client = _client()
    _mk(client, available=True)
    _mk(client, available=False)
    r = client.get("/products?available=true")
    assert r.status_code == status.HTTP_200_OK
    body = r.get_json()
    assert all(p["available"] is True for p in body)


# ------------------ ERROR / EDGE CASES ------------------ #
def test_create_product_bad_request():
    client = _client()
    # Falta 'name' -> DataValidationError -> 400
    r = client.post(
        "/products",
        json={
            "description": "x",
            "price": "1.00",
            "available": True,
            "category": "FOOD",
        },
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST


def test_update_product_not_found():
    client = _client()
    r = client.put(
        "/products/999999",
        json={
            "name": "X",
            "description": "x",
            "price": "1.00",
            "available": True,
            "category": "FOOD",
        },
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_update_product_bad_request():
    client = _client()
    pid = _mk(client)
    # available mal tipeado -> 400
    r = client.put(
        f"/products/{pid}",
        json={
            "name": "X",
            "description": "x",
            "price": "1.00",
            "available": "yes",
            "category": "FOOD",
        },
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST


def test_list_products_invalid_category():
    client = _client()
    _mk(client)
    r = client.get("/products?category=NOPE")
    assert r.status_code == status.HTTP_400_BAD_REQUEST


def test_admin_reset_endpoint():
    client = _client()
    _mk(client)
    _mk(client)
    r = client.delete("/admin/reset")
    assert r.status_code == status.HTTP_200_OK
    r = client.get("/products")
    assert r.status_code == status.HTTP_200_OK
    assert len(r.get_json()) == 0
