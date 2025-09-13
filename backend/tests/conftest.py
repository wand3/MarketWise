import pytest
import os
import json
from faker import Faker
from config import TestConfig
from webapp.models.product import ProductListing, PriceHistory
from webapp import db, create_app

# Configure testing environment before app initialization
os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture
def db_session():
    # Use Flask-SQLAlchemy's database operations
    app = create_app(TestConfig)
    with app.app_context():
        # Create all tables
        db.create_all()

        yield app  # Use Flask-SQLAlchemy's session
        # Clean up after test
        db.session.remove()
        db.drop_all()


# Create a test app instance with test configuration
@pytest.fixture
def client(db_session):
    return db_session.test_client()
    # app = create_app(TestConfig)
    # with app.app_context():
    #     with app.test_client() as client:
    #         yield client


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def sample_products(tmp_path):
    """Creates a temporary JSON file with sample product data."""
    products = [
        {
            "product_name": "Test Product",
            "image_url": "http://example.com/image.jpg",
            "source": "test_source",
            "product_url": "http://example.com/product",
            "current_price": "$19.99",
            "search_text": "test",
            "currency": "$"
        }
    ]
    # file_path = tmp_path / "test_products.json"
    # with open(file_path, "w") as f:
    #     json.dump(products, f)
    # return file_path
    p = tmp_path / "products.json"
    p.write_text(json.dumps(products))
    return p
