import random
import time
from collections.abc import Iterator

import items
import scrapy
from constants import ALLOWED_DOMAINS, START_URLS
from itemadapter import ItemAdapter
from loguru import logger


class ProductsSpider(scrapy.Spider):
    """Spider for crawling urparts.com to extract product information."""

    name = "products-scraper"
    start_urls = START_URLS
    allowed_domains = ALLOWED_DOMAINS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items_scraped = 0
        logger.info(f"Starting {self.name} spider")

    def start_requests(self) -> Iterator[scrapy.Request]:
        """Generate initial requests with random delay to be more respectful to the server."""
        for url in self.start_urls:
            # Add a small random delay before starting
            time.sleep(random.uniform(1.0, 3.0))
            yield scrapy.Request(url, callback=self.parse, errback=self.handle_error)

    def parse(self, response) -> Iterator[scrapy.Request]:  # noqa: ANN001
        """Initial parsing entrypoint.

        Parse the homepage and, for each 'make' found, yield a new request and assign
        it to the next parsing step (parse_category()).

        Args:
            response: the http response from the request.

        Returns:
            An iterator of further scrapy request objects.
        """
        logger.info(f"Parsing makes from {response.url}")
        make_count = 0

        try:
            make_elements = response.css("div.allmakes li")

            if not make_elements:
                logger.warning(f"No makes found at {response.url}")
                return

            for li in make_elements:
                make = li.css("a::text").get()
                if not make:
                    continue

                make = make.strip()
                make_href = li.css("a::attr(href)").get()
                if not make_href:
                    logger.warning(f"No href found for make: {make}")
                    continue

                make_count += 1
                product = {"make": make}

                yield scrapy.Request(
                    response.urljoin(make_href),
                    callback=self.parse_category,
                    errback=self.handle_error,
                    meta={"product": product, "depth": 1},
                )

            logger.info(f"Found {make_count} makes to process")

        except Exception as e:
            logger.error(f"Error parsing makes: {str(e)}")

    def parse_category(self, response) -> Iterator[scrapy.Request]:  # noqa: ANN001
        """Second parse step.

        On this make's page, parse out all the product categories and initialize further scrapes
        for each one of them.

        Args:
            response: the http response from the request.

        Returns:
            An iterator of further scrapy request objects.
        """
        product = response.meta.get("product", {})
        logger.info(
            f"Parsing categories for make: {product.get('make')} from {response.url}"
        )

        try:
            category_elements = response.css("div.allcategories li")

            if not category_elements:
                logger.warning(f"No categories found for make: {product.get('make')}")
                return

            for li in category_elements:
                category = li.css("a::text").get()
                if not category:
                    continue

                # Convert to lowercase for consistency
                category = category.strip().lower()
                category_href = li.css("a::attr(href)").get()
                if not category_href:
                    logger.warning(f"No href found for category: {category}")
                    continue

                new_product = dict(product)
                new_product["category"] = category

                yield scrapy.Request(
                    response.urljoin(category_href),
                    callback=self.parse_model,
                    errback=self.handle_error,
                    meta={"product": new_product, "depth": 2},
                )

        except Exception as e:
            logger.error(f"Error parsing categories: {str(e)}")

    def parse_model(self, response) -> Iterator[scrapy.Request]:  # noqa: ANN001
        """Third parse step.

        On this category's page, parse out all the product models and initialize further scrapes
        for each one of them.

        Args:
            response: the http response from the request.

        Returns:
            An iterator of further scrapy request objects.
        """
        product = response.meta.get("product", {})
        logger.info(
            f"Parsing models for make: {product.get('make')}, category: {product.get('category')}"
        )

        try:
            model_elements = response.css("div.allmodels li")

            if not model_elements:
                logger.warning(
                    f"No models found for make: {product.get('make')}, category: {product.get('category')}"
                )
                return

            for li in model_elements:
                model = li.css("a::text").get()
                if not model:
                    continue

                model = model.strip()
                model_href = li.css("a::attr(href)").get()
                if not model_href:
                    logger.warning(f"No href found for model: {model}")
                    continue

                new_product = dict(product)
                new_product["model"] = model

                yield scrapy.Request(
                    response.urljoin(model_href),
                    callback=self.parse_part,
                    errback=self.handle_error,
                    meta={"product": new_product, "depth": 3},
                )

        except Exception as e:
            logger.error(f"Error parsing models: {str(e)}")

    def parse_part(self, response) -> Iterator[items.ProductItem]:  # noqa: ANN001
        """Fourth parse step.

        On this model's page, parse out all the parts and yield ProductItem objects
        with all the collected information.

        Args:
            response: the http response from the request.

        Returns:
            An iterator of ProductItem objects.
        """
        product = response.meta.get("product", {})
        make = product.get("make", "")
        category = product.get("category", "")
        model = product.get("model", "")

        logger.info(
            f"Parsing parts for make: {make}, category: {category}, model: {model}"
        )

        try:
            part_elements = response.css("div.allparts li")

            if not part_elements:
                logger.warning(
                    f"No parts found for make: {make}, category: {category}, model: {model}"
                )
                return

            for li in part_elements:
                part_number_text = li.css("a::text").get()
                if not part_number_text:
                    continue

                # Extract part number from text
                try:
                    part_number = part_number_text.split("-")[0].strip()
                except (IndexError, AttributeError):
                    logger.warning(
                        f"Could not parse part number from: {part_number_text}"
                    )
                    part_number = part_number_text.strip()

                # Parse part type, handling potential missing data
                try:
                    part_type = li.css("a span::text").get()
                    part_type = part_type.strip().lower() if part_type else None
                except AttributeError:
                    part_type = None

                # Create and validate the item
                product_item = items.ProductItem(
                    make=make,
                    category=category,
                    model=model,
                    part_type=part_type,
                    part_number=part_number,
                )

                # Validate item
                if self.validate_item(product_item):
                    self.items_scraped += 1
                    return product_item

        except Exception as e:
            logger.error(f"Error parsing parts: {str(e)}")

    def validate_item(self, item: items.ProductItem) -> bool:
        """Validate required fields in the item.

        Args:
            item: The item to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        adapter = ItemAdapter(item)
        required_fields = ["make", "model", "part_number"]

        for field in required_fields:
            if not adapter.get(field):
                logger.warning(f"Missing required field {field} in item")
                return False
        return True

    def handle_error(self, failure) -> None:  # noqa: ANN001
        """Handle request failures gracefully.

        Args:
            failure: The failure information.
        """
        request = failure.request
        logger.error(f"Request failed: {request.url}, error: {repr(failure)}")

    def closed(self, reason: str) -> None:
        """Called when the spider is closed.

        Args:
            reason: The reason for closing.
        """
        logger.info(
            f"Spider closed: {reason}. Total items scraped: {self.items_scraped}"
        )
