# from typing import Any
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy import ForeignKey, String, Float, DateTime
# from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .. import db
from datetime import datetime


class ProductListing(db.Model):
    __tablename__ = "product_listings"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    source = db.Column(db.String(255))
    url = db.Column(db.String(500), nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    search_text = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    price_history = db.relationship(
        "PriceHistory",
        back_populates="listing",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Listing {self.product_name}, source: {self.source}, price: {self.currency}{self.current_price} >"


class PriceHistory(db.Model):
    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("product_listings.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tracked = db.Column(db.Boolean, default=True)

    listing = db.relationship("ProductListing", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory {self.price} at {self.timestamp} {self.listing}>"
