import pytest
import os
from faker import Faker
from config import TestConfig
from product import ProductListing, PriceHistory, Base
from app import db, app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

# Configure testing environment before app initialization
os.environ['FLASK_ENV'] = 'testing'
if os.environ.get('FLASK_ENV') == 'testing':
    app.config.from_object(TestConfig)


@pytest.fixture(scope="function")
def db_session():
    # Use in-memory SQLite DB
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    yield session  # this is where the testing happens

    session.close()
    Base.metadata.drop_all(bind=engine)
    clear_mappers()


@pytest.fixture
def fake():
    return Faker()
