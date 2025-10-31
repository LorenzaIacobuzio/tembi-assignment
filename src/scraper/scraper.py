import random
import re
import json
from playwright.async_api import async_playwright
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def scrape_site(site_config):
    base_url = site_config["base"]
    result = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Go to homepage
        await page.goto(base_url)

        # Find collections
        collection_links = await page.locator(
            "a[href*='/collections/']"
        ).element_handles()
        collections = list({await el.get_attribute("href") for el in collection_links})
        collections = [c for c in collections if c and "/collections/" in c]

        if not collections:
            await browser.close()
            return None

        collection_url = random.choice(collections)
        if not collection_url.startswith("http"):
            collection_url = base_url.rstrip("/") + collection_url
        await page.goto(collection_url)

        # Find products
        product_links = await page.locator("a[href*='/products/']").element_handles()
        products = list({await el.get_attribute("href") for el in product_links})
        products = [p for p in products if p and "/products/" in p]

        if not products:
            await browser.close()
            return None

        product_url = random.choice(products)
        if not product_url.startswith("http"):
            product_url = base_url.rstrip("/") + product_url
        await page.goto(product_url)

        # Fetch product title
        title = await page.locator(
            "h1.product__title, h1.title, h1"
        ).first.text_content()
        title = title.strip() if title else "Unknown"

        # Fetch product price
        price_text = await page.locator(
            ".price, span[itemprop='price'], .product__price"
        ).first.text_content()
        price_text = price_text.strip() if price_text else "0"

        # Detect currency
        currency = None
        if "kr" in price_text.lower():
            currency = "DKK"
        elif "$" in price_text:
            currency = "USD"
        elif "€" in price_text:
            currency = "EUR"

        # Extract numeric value
        cleaned = re.sub(r"[^\d,\.]", "", price_text)
        if "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")
        try:
            price_numeric = float(cleaned)
        except ValueError:
            price_numeric = 0.0

        shipping_providers = []

        # Handle size selector and add to cart
        try:
            add_to_cart_btn = page.locator(
                "button[name='add'], form[action*='/cart/add'] button"
            )
            await add_to_cart_btn.first.click()
            await page.wait_for_timeout(1000)

            # Select first available size only
            available_sizes = page.locator(
                "li.select-option.available label.swatch-anchor"
            )
            if await available_sizes.count() > 0:
                first_available = available_sizes.first
                await first_available.click()
                await page.wait_for_timeout(800)

                # Click Add to Cart again inside modal or product form
                add_to_cart_modal = page.locator(
                    "button[name='add'], form[action*='/cart/add'] button"
                )
                if await add_to_cart_modal.count() > 0:
                    await add_to_cart_modal.first.click()
                    await page.wait_for_timeout(1500)

            # Verify cart contents
            await page.goto(base_url + "/cart.js")
            cart_content = await page.locator("body").text_content()
            json.loads(cart_content)

            # Retrieve and normalize shipping providers
            try:
                shipping_url = f"{base_url}/cart/shipping_rates.json?shipping_address[zip]=8000&shipping_address[country]=Denmark"
                await page.goto(shipping_url)
                shipping_text = await page.locator("body").text_content()
                shipping_data = json.loads(shipping_text)

                if "shipping_rates" in shipping_data:
                    raw_names = [
                        rate["name"] for rate in shipping_data["shipping_rates"]
                    ]

                    normalized = [
                        re.split(r"[-,]", name)[0].strip() for name in raw_names
                    ]

                    # Deduplicate
                    shipping_providers = sorted(list(set(normalized)))
                else:
                    logger.warning("[-] No shipping info in response:", shipping_data)

            except Exception as e:
                logger.error("[-] Failed to fetch shipping info:", e)
                shipping_providers = []

        except Exception as e:
            logger.error("[-] Add to cart / shipping failed:", e)

        await browser.close()

        result = {
            "title": title,
            "price": price_numeric,
            "currency": currency,
            "url": product_url,
            "shipping_providers": shipping_providers,
        }

        return result
