import pytest
import os
from faker import Faker
from config import TestConfig
from webapp.models.product import ProductListing, PriceHistory
from webapp import db, create_app

# Configure testing environment before app initialization
os.environ['FLASK_ENV'] = 'testing'
if os.environ.get('FLASK_ENV') == 'testing':
    create_app(TestConfig)


# Create a test app instance with test configuration
@pytest.fixture(scope='session')
def test_app():
    app = create_app(TestConfig)  # Use your create_app function if available
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def db_session(test_app):
    # Use Flask-SQLAlchemy's database operations
    with test_app.app_context():
        # Create all tables
        db.create_all()

        yield db.session  # Use Flask-SQLAlchemy's session

        # Clean up after test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def fake():
    return Faker()
