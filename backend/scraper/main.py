import argparse
import asyncio
import json
import os
import random
from logger import setup_logger
from amazon import scrape_amazon_async
from aliexpress import scrape_aliexpress_async


logger = setup_logger("main", "DEBUG", "scraper.log")

ALIEXPRESS = "https://aliexpress.com"
AMAZON = "https://amazon.com"

URLS = {
    AMAZON: {
        "search_field_query": 'input[name="field-keywords"]',
        "search_button_query": 'input[value="Go"]',
        "product_selector": "div.s-card-container"
    },
    ALIEXPRESS: {
        "search_field_query": 'input[id="search-words"]',
        "search_button_query": 'input[title="submit"]',
        "product_selector": ""
    }
}

available_urls = URLS.keys()


async def run_scrapers_async(search):
    aliexpress_data = await scrape_aliexpress_async(search)
    amazon_data = await scrape_amazon_async(search)


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


if __name__ == "__main__":
    args = parse_arguments()
    print(f"Starting scrapers for search terms: {', '.join(args.search)}")

    # Run the async scraper
    asyncio.run(run_scrapers_async(args.search))

