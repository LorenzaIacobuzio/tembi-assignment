import os

from flask import Flask, jsonify

from src.database.db import SessionLocal
from src.models import Product

app = Flask(__name__)


@app.route("/products", methods=["GET"])
def list_products():
    session = SessionLocal()
    try:
        products = session.query(Product).all()
        out = []
        for p in products:
            out.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "price": p.price,
                    "currency": p.currency,
                    "url": p.url,
                    "scraped_at": p.scraped_at.isoformat() if p.scraped_at else None,
                    "shipping_providers": [s.name for s in p.shipping_providers],
                }
            )
        return jsonify(out)
    finally:
        session.close()


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
