from sqlalchemy import ForeignKey, String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import datetime
from . import Base


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    listings: Mapped[list["ProductListing"]] = relationship(back_populates="platform")

    def __repr__(self):
        return f"<Platform {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)

    listings: Mapped[list["ProductListing"]] = relationship(back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductListing(Base):
    __tablename__ = "product_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=True)

    product: Mapped["Product"] = relationship(back_populates="listings")
    platform: Mapped["Platform"] = relationship(back_populates="listings")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="listing", cascade="all, delete"
    )

    def __repr__(self):
        return f"<Listing {self.title} on {self.platform.name}>"


class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("product_listings.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    listing: Mapped["ProductListing"] = relationship(back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory {self.price} at {self.timestamp}>"

