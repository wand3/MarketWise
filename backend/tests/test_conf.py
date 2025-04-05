import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from models.product import Base
from models.product import ProductListing, PriceHistory

from faker import Faker


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
