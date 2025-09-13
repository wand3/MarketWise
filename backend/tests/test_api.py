import pytest
import json
from config import TestConfig
from webapp.models.product import ProductListing, PriceHistory
from webapp import db, create_app
from .conftest import client


def test_404(client):
    response = client.get(
        '/wrong/url'
    )
    print(response)
    assert response.status_code == 404


def test_load_products_missing_file(client):
    payload = {
        "file_path": "nonexistent/path/to/file.json"
    }
    response = client.post(
        "/api/load-products",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "JSON file not found" in data["message"]


def test_load_products_empty_file(client, tmp_path):
    empty_file = tmp_path / "empty.json"
    with open(empty_file, "w") as f:
        json.dump([], f)

    payload = {
        "file_path": str(empty_file)
    }
    response = client.post(
        "/api/load-products",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is True
    assert data["loaded_count"] == 0
    assert "No products found" in data["message"]


def test_load_products_success(client, sample_products):
    payload = {
        "file_path": str(sample_products),
        "clear_after_load": True
    }
    response = client.post(
        "/api/load-products",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["loaded_count"] == 1
    assert "Successfully loaded" in data["message"]
