import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path
import re
from .logger import setup_logger
from .amazon import scrape_amazon_async
from .aliexpress import scrape_aliexpress_async


logger = setup_logger("main", "DEBUG", "scraper.log")


async def run_scrapers_async(search):
    aliexpress_data = await scrape_aliexpress_async(search)
    amazon_data = await scrape_amazon_async(search)

    if aliexpress_data and amazon_data:
        return
    return False


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Run product scrapers with custom search terms')
    parser.add_argument(
        '--search',
        nargs='+',
        required=True,
        help='item to be searched'
    )
    return parser.parse_args()


def parse_price(s: str) -> tuple[str, float]:
    """
    Splits a string like 'NGN4,088.24' or '$4088.24' into
    ('NGN', 4088.24) or ('$', 4088.24).
    """
    # This regex says:
    #  ^\s*              optional leading whitespace
    #  ([^\d.,-]+)?      capture any non‑digit/non‑dot/non‑comma chars (the currency)
    #  \s*               optional whitespace
    #  ([\d,]+(?:\.\d+)?)  capture the number, allowing commas and an optional decimal part
    #  \s*$              optional trailing whitespace
    m = re.match(r'^\s*([^\d.,-]+)?\s*([\d,]+(?:\.\d+)?)\s*$', s)
    if not m:
        raise ValueError(f"Unrecognized format: {s!r}")

    currency = m.group(1) or ''
    num_str = m.group(2).replace(',', '') or ''
    if isinstance(currency, str) and float(num_str):
        return currency, float(num_str)


def load_products_from_json(json_path, search):
    """Load products from JSON file to database and clear file on success"""
    from ..app import app, db
    from ..product import ProductListing

    with app.app_context():
        try:
            # Read products from JSON file
            if not json_path.exists():
                logger.warning(f"JSON file not found: {json_path}")
                return 0
            with open(json_path, 'r') as f:
                products = json.load(f)

            if not products:
                logger.info("No products found in JSON file")
                return 0

            products_added_count = 0
            for item in products:
                # Standardize keys from JSON to model attributes
                product_name = item.get('product_name')
                product_price = item.get('product_price')
                image_url = item.get('image_url')
                product_url = item.get('product_url')
                source = item.get('source')

                # Basic validation
                if not all([product_name, product_price, product_url, source]):
                    print(f"Skipping incomplete product data: {item}")
                    continue

                # --- MODIFICATION STARTS HERE ---
                price = 0.0  # Default price
                currency = None  # Default currency
                try:
                    price, currency = parse_price(product_price)
                except ValueError as e:
                    # Log the specific price parsing error
                    logger.warning(f"Failed to parse price for product '{product_name}' ({product_url}): {e}")
                    # Decide how to proceed:
                    continue  # This will skip the rest of the loop for this item
                    # Option 2: Keep price as 0.0 and currency as None, then proceed to add the product
                # --- MODIFICATION ENDS HERE ---

                # Fix relative URLs from AliExpress if necessary
                if source.lower() == 'aliexpress' and product_url and product_url.startswith('//'):
                    product_url = 'https:' + product_url
                if source.lower() == 'aliexpress' and image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url

                # Fix relative URLs from amazon if necessary
                if source.lower() == 'amazon' and product_url and product_url.startswith('/'):
                    product_url = 'https:/' + product_url

                # if not existing_product:
                try:
                    new_product = ProductListing(
                        product_name=product_name,
                        image=image_url,
                        source=source,
                        url=product_url,
                        current_price=price,  # Assign the new field
                        currency=currency,
                        created_at=datetime.utcnow(),
                        search_text=str(search)
                    )
                    db.session.add(new_product)
                    logger.info(new_product)
                    products_added_count += 1
                except Exception as e:
                    logger.error(f"Error adding single product to db {e}")
                    print(f"Product already exists (URL: {product_url}). Skipping.")

            db.session.commit()
            print(f"Successfully loaded {products_added_count} new products from {file_path}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database load failed: {str(e)}")
            return 0


if __name__ == "__main__":
    args = parse_arguments()
    print(f"Starting scrapers for search terms: {', '.join(args.search)}")

    # result path
    base_folder = Path(__file__).resolve().parent.parent
    output_dir = base_folder / 'scraper'
    file_path = output_dir / "result.json"

    load_products_from_json(file_path, args.search)


    # Run the async scraper
    # asyncio.run(run_scrapers_async(args.search))

