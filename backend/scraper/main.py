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
    # amazon_data = await scrape_amazon_async(search)
    #
    # if amazon_data:
    #     return
    if aliexpress_data:
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


if __name__ == "__main__":
    args = parse_arguments()
    print(f"Starting scrapers for search terms: {', '.join(args.search)}")

    # result path
    base_folder = Path(__file__).resolve().parent.parent
    output_dir = base_folder / 'scraper'
    file_path = output_dir / "result.json"

    # load_products_from_json(file_path, args.search)
    try:

        # Run the async scraper
        asyncio.run(run_scrapers_async(args.search))
    except Exception as e:
        print(e)
