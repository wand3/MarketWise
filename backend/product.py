from typing import Any

from sqlalchemy import ForeignKey, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProductListing(Base):
    __tablename__ = "product_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=True)
    search_text: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="listing", cascade="all, delete"
    )

    def __init__(self, product_name, image, source, url, current_price, currency, search_text, created_at):
        super(Base).__init__()
        self.product_name = product_name
        self.image = image
        self.source = source
        self.url = url
        self.current_price = current_price
        self.currency = currency
        self.search_text = search_text
        self.created_at = created_at

    def __repr__(self):
        return f"<Listing {self.product_name}, source: {self.source}, price: {self.currency}{self.current_price} >"


class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("product_listings.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    listing: Mapped["ProductListing"] = relationship(back_populates="price_history")
    tracked: Mapped[bool] = mapped_column(default=True)


    def __repr__(self):
        return f"<PriceHistory {self.price} at {self.timestamp} {self.listing}>"
