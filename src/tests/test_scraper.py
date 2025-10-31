import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.scraper.scraper import scrape_site


@pytest.mark.asyncio
async def test_scrape_site_basic():
    site_config = {"base": "https://example.com"}

    mock_collection_el = AsyncMock()
    mock_collection_el.get_attribute = AsyncMock(
        return_value="/collections/test-collection"
    )

    mock_product_el = AsyncMock()
    mock_product_el.get_attribute = AsyncMock(return_value="/products/test-product")

    mock_locator = AsyncMock()
    mock_locator.element_handles = AsyncMock(
        side_effect=[
            [mock_collection_el],
            [mock_product_el],
        ]
    )
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.first.text_content = AsyncMock(
        side_effect=[
            "Test Product",
            "100 kr",
        ]
    )
    mock_locator.nth.return_value.click = AsyncMock()

    async def body_text_side_effect():
        url = mock_page.goto.call_args[0][0]
        if url.endswith("/cart.js"):
            return '{"token":"abc","items":[{"title":"Test Product"}]}'
        elif "shipping_rates.json" in url:
            return '{"shipping_rates":[{"name":"DHL - Copenhagen"},{"name":"UPS - Aarhus"},{"name":"DHL - Aarhus"}]}'
        return "Unknown"

    mock_body_locator = AsyncMock()
    mock_body_locator.text_content.side_effect = body_text_side_effect

    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.locator = MagicMock(
        side_effect=lambda selector: (
            mock_locator if "body" not in selector else mock_body_locator
        )
    )

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_async_playwright_cm = AsyncMock()
    mock_async_playwright_cm.__aenter__.return_value = mock_playwright
    mock_async_playwright_cm.__aexit__.return_value = None

    with patch(
        "src.scraper.scraper.async_playwright", return_value=mock_async_playwright_cm
    ):
        result = await scrape_site(site_config)

    assert result["title"] == "Test Product"
    assert result["price"] == 100.0
    assert result["currency"] == "DKK"
    assert sorted(result["shipping_providers"]) == ["DHL", "UPS"]


@pytest.mark.asyncio
async def test_scrape_site_no_collections():
    site_config = {"base": "https://example.com"}

    mock_locator = AsyncMock()
    mock_locator.element_handles = AsyncMock(return_value=[])
    mock_locator.count = AsyncMock(return_value=0)

    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_async_playwright_cm = AsyncMock()
    mock_async_playwright_cm.__aenter__.return_value = mock_playwright
    mock_async_playwright_cm.__aexit__.return_value = None

    with patch(
        "src.scraper.scraper.async_playwright", return_value=mock_async_playwright_cm
    ):
        result = await scrape_site(site_config)

    assert result is None


@pytest.mark.asyncio
async def test_scrape_site_invalid_price():
    site_config = {"base": "https://example.com"}

    mock_collection_el = AsyncMock()
    mock_collection_el.get_attribute = AsyncMock(return_value="/collections/test")
    mock_product_el = AsyncMock()
    mock_product_el.get_attribute = AsyncMock(return_value="/products/test")

    mock_locator = AsyncMock()
    mock_locator.element_handles = AsyncMock(
        side_effect=[[mock_collection_el], [mock_product_el]]
    )
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.first.text_content = AsyncMock(
        side_effect=[
            "Test Product",
            "Not a price",
        ]
    )
    mock_locator.nth.return_value.click = AsyncMock()

    async def body_text_side_effect():
        url = mock_page.goto.call_args[0][0]
        if url.endswith("/cart.js"):
            return '{"token":"abc","items":[{"title":"Test Product"}]}'
        elif "shipping_rates.json" in url:
            return '{"shipping_rates":[{"name":"DHL - Copenhagen"}]}'
        return "Unknown"

    mock_body_locator = AsyncMock()
    mock_body_locator.text_content.side_effect = body_text_side_effect

    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.locator = MagicMock(
        side_effect=lambda selector: (
            mock_locator if "body" not in selector else mock_body_locator
        )
    )

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_async_playwright_cm = AsyncMock()
    mock_async_playwright_cm.__aenter__.return_value = mock_playwright
    mock_async_playwright_cm.__aexit__.return_value = None

    with patch(
        "src.scraper.scraper.async_playwright", return_value=mock_async_playwright_cm
    ):
        result = await scrape_site(site_config)

    assert result["price"] == 0.0
    assert result["currency"] is None
    assert result["shipping_providers"] == ["DHL"]


@pytest.mark.asyncio
async def test_scrape_site_no_shipping():
    site_config = {"base": "https://example.com"}

    mock_collection_el = AsyncMock()
    mock_collection_el.get_attribute = AsyncMock(return_value="/collections/c")
    mock_product_el = AsyncMock()
    mock_product_el.get_attribute = AsyncMock(return_value="/products/p")

    mock_locator = AsyncMock()
    mock_locator.element_handles = AsyncMock(
        side_effect=[[mock_collection_el], [mock_product_el]]
    )
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.first.text_content = AsyncMock(side_effect=["Test Product", "100 kr"])
    mock_locator.nth.return_value.click = AsyncMock()

    async def body_text_side_effect():
        return '{"shipping_rates": []}'

    mock_body_locator = AsyncMock()
    mock_body_locator.text_content.side_effect = body_text_side_effect

    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.locator = MagicMock(
        side_effect=lambda selector: (
            mock_locator if "body" not in selector else mock_body_locator
        )
    )

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_async_playwright_cm = AsyncMock()
    mock_async_playwright_cm.__aenter__.return_value = mock_playwright
    mock_async_playwright_cm.__aexit__.return_value = None

    with patch(
        "src.scraper.scraper.async_playwright", return_value=mock_async_playwright_cm
    ):
        result = await scrape_site(site_config)

    assert result["shipping_providers"] == []
