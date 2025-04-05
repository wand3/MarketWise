from models.product import ProductListing, PriceHistory
from .test_conf import db_session, fake
from datetime import datetime


def test_listing_creation(db_session, fake):
    listing = ProductListing(
        product_name=fake.catch_phrase(),
        image=fake.image_url(),
        source=fake.company(),
        url=fake.url(),
        current_price=round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
        currency=fake.currency_code(),
        search_text=" ".join(fake.words(nb=3))
    )

    db_session.add(listing)
    db_session.commit()

    assert listing.id is not None
    assert listing.created_at is not None
    assert listing.current_price > 0
    assert isinstance(listing.source, str)


def test_price_history_tracking(db_session, fake):
    listing = ProductListing(
        product_name=fake.catch_phrase(),
        image=fake.image_url(),
        source=fake.company(),
        url=fake.url(),
        current_price=round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
        currency=fake.currency_code(),
        search_text=" ".join(fake.words(3))
    )
    db_session.add(listing)
    db_session.flush()  # Get listing.id before commit

    history = PriceHistory(
        listing_id=listing.id,
        price=round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2)
    )

    db_session.add(history)
    db_session.commit()

    fetched = db_session.get(ProductListing, listing.id)
    assert fetched.price_history[0].price > 0
    assert fetched.price_history[0].tracked is True
