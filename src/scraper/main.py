import asyncio
import logging
import os
import time

from src.database.db import SessionLocal
from src.models import Product, ShippingProvider
from src.scraper.config import SITES
from src.scraper.scraper import scrape_site

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    target = os.getenv("TARGET_SITE")
    sites = SITES
    if target:
        if target in sites:
            sites = {target: sites[target]}
        else:
            logger.warning(
                "TARGET_SITE %s not in config, defaulting to all sites", target
            )

    for name, conf in sites.items():
        logger.info("Scraping site: %s", name)
        try:
            result = asyncio.run(scrape_site(conf))
            if result:
                logger.info(
                    "Scraped product: %s | Price: %s %s",
                    result["title"],
                    result["price"],
                    result["currency"],
                )
                with SessionLocal() as session:
                    product = Product(
                        title=result["title"],
                        price=result["price"],
                        currency=result["currency"],
                        url=result["url"],
                    )
                    session.add(product)
                    session.commit()
                    logger.info("Product saved to DB: %s", product.id)

                    for providerName in result["shipping_providers"]:
                        provider = (
                            session.query(ShippingProvider)
                            .filter_by(name=providerName)
                            .first()
                        )
                        if not provider:
                            provider = ShippingProvider(name=providerName)
                            session.add(provider)
                            session.commit()
                        if provider not in product.shipping_providers:
                            product.shipping_providers.append(provider)
                    session.commit()
                    logger.info(
                        "Linked shipping providers: %s", result["shipping_providers"]
                    )
            else:
                logger.warning("No product scraped from site %s", name)
        except Exception as e:
            logger.exception("Error scraping %s: %s", name, e)
        time.sleep(2)


if __name__ == "__main__":
    main()
