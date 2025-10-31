from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


product_shipping = Table(
    "product_shipping",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("shipping_id", ForeignKey("shipping_providers.id"), primary_key=True),
)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(8), nullable=True)
    url = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    shipping_providers = relationship(
        "ShippingProvider", secondary=product_shipping, back_populates="products"
    )


class ShippingProvider(Base):
    __tablename__ = "shipping_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    products = relationship(
        "Product", secondary=product_shipping, back_populates="shipping_providers"
    )
