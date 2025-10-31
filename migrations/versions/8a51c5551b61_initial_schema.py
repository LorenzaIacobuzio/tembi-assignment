"""initial schema

Revision ID: 8a51c5551b61
Revises:
Create Date: 2025-10-31 10:17:29.036296

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8a51c5551b61"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create products table
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("currency", sa.String(8), nullable=True),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column(
            "scraped_at",
            sa.DateTime,
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Create shipping_providers table
    op.create_table(
        "shipping_providers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column(
            "scraped_at",
            sa.DateTime,
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Create association table for many-to-many relationship
    op.create_table(
        "product_shipping",
        sa.Column(
            "product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True
        ),
        sa.Column(
            "shipping_id",
            sa.Integer,
            sa.ForeignKey("shipping_providers.id"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop tables in reverse order
    op.drop_table("product_shipping")
    op.drop_table("shipping_providers")
    op.drop_table("products")
