from sqlalchemy import ForeignKey, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
# from . import Base

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

    def __repr__(self):
        return f"<Listing {self.product_name}, source: {self.source}, price: {self.currency}{self.current_price} >"


class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("product_listings.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    listing: Mapped["ProductListing"] = relationship(back_populates="price_history")
    tracked: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f"<PriceHistory {self.price} at {self.created_at}>"
