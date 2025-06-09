import asyncio
import hashlib
import random
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import setup_logger
import json
import os

logger = setup_logger("amazon", "DEBUG", "scraper.log")
delay = random.uniform(3, 6)

AMAZON = "https://amazon.com"

URLS = {
    AMAZON: {
        "search_field_query": 'input[name="field-keywords"]',
        "search_button_query": 'input[value="Go"]',
        "product_selector": "div.s-card-container"
    }
}


def search(metadata, driver, search_text):
    logger.info(f"Searching for {search_text} on {driver.current_url}")

    search_field_query = metadata.get("search_field_query")
    search_button_query = metadata.get("search_button_query")

    if search_field_query and search_button_query:
        logger.info("Filling input field")

        # Wait for the search box to appear and type into it
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, search_field_query))
        )
        search_box.clear()
        driver.implicitly_wait(random.randint(3, 6))  # seconds
        search_box.send_keys(search_text)

        logger.info("Pressing search button")

        # Wait for the search button to appear and click it
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, search_button_query))
        )
        search_button.click()

        # Wait for the page to load (basic wait, can be customized)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("Search result success")
    else:
        raise Exception("Could not search: missing selectors.")

    return driver


def get_stock(soup):
    # Find all divs with the specified class
    all_divs = soup.find_all("div", attrs={"role": "listitem"})
    logger.info(f"divs on scroll: {len(all_divs)}")

    return all_divs


def hash_product(product):
    """Create unique hash for product based on its URL and name"""
    return hashlib.md5(
        (product["product_url"] + product["product_name"]).encode()
    ).hexdigest()


def get_product(driver):
    # Get the page content
    html_code = driver.page_source
    soup = BeautifulSoup(html_code, 'html.parser')
    listitems = get_stock(soup)  # Assuming this function is defined elsewhere

    current_page_products = []
    seen_products = set()

    # Create the output directory if it doesn't exist
    base_folder = Path(__file__).resolve().parent.parent
    output_dir = base_folder / 'scraper'
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "result.json"

    # Load existing products if file exists
    existing_products = []
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                existing_products = json.load(f)
                # Create set of existing product hashes for deduplication
                seen_products = {hash_product(p) for p in existing_products}
        except json.JSONDecodeError:
            logger.warning("JSON file is empty/corrupted. Starting fresh.")

    # Process current page items
    for item in listitems:
        product_image = item.find("img", class_="s-image")
        product_name = item.find("h2", class_="a-size-medium")
        product_link = item.find("a", class_="a-link-normal")
        product_price = item.find("span", class_="a-offscreen")

        product = {
            "product_name": product_name.text if product_name else "N/A",
            "product_price": product_price.text if product_price else "N/A",
            "image_url": product_image.get('src') if product_image else "N/A",
            "product_url": "/".join(product_link.get('href').split("/")[:4]) if product_link else "N/A",
            "source": "Amazon"
        }

        # Create unique hash for the product
        product_hash = hash_product(product)

        # Check for duplicates
        if product_hash not in seen_products:
            seen_products.add(product_hash)
            current_page_products.append(product)
            logger.info(f'New product added: {product["product_name"]}')
        else:
            logger.info(f'Duplicate skipped: {product["product_name"]}')

    # Merge with existing products
    all_products = existing_products + current_page_products

    # Save to JSON
    with open(file_path, 'w') as f:
        json.dump(all_products, f, indent=2)

    logger.info(f'Total products in file: {len(all_products)}')
    logger.info(f'New products added: {len(current_page_products)}')
    return current_page_products


# def get_product(driver):
#     # Get the page content
#     html_code = driver.page_source
#     # get all searched products on each page scroll
#     soup = BeautifulSoup(html_code, 'html.parser')
#     listitems = get_stock(soup)
#     # logger.info(listitems)
#
#     products = []
#     product = {}
#     for item in listitems:
#         product_image = item.find("img", class_="s-image")
#         product_name = item.find("h2", class_="a-size-medium")
#         product_link = item.find("a", class_="a-link-normal")
#         product_price = item.find("span", class_="a-offscreen")
#
#         if product_name:
#             name = product_name.text
#             product["product_name"] = name
#         if product_price:
#             price = product_price.text
#             product["product_price"] = price
#         if product_image:
#             href = product_image.get('src')
#             product["image_url"] = href
#         if product_link:
#             href = product_link.get('href')
#             product["product_url"] = "/".join(href.split("/")[:4])
#         product["source"] = "Amazon"
#         logger.info(f'Each product in page {product}')
#
#         products.append(product)
#
#     # Save to json
#     base_folder = Path(__name__).resolve().parent
#     file_path = f'/{base_folder}/backend/scraper/result.json'
#     with open(file_path, 'w') as f:
#         json.dump(products, f)
#     logger.info(f'All product in page {len(products)}')
#     logger.info(f'All product in page {set(products)}')
#     return products


# scroll to pagination part of page
def scroll_page(driver):
    logger.info("Scroll in")

    page_visited = 0
    while True:
        try:
            # Wait for the search button to appear and click it
            dismiss_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@data-action-type="DISMISS"]'))
            )
            logger.info("dismiss success")

            if dismiss_button:
                dismiss_button.click()
                logger.info("click dismiss success")
        except Exception as e:
            pass
            # Wait for next button to be clickable
        finally:
            scroll_count = 15
            height = 0
            for i in range(scroll_count):
                try:
                    time.sleep(delay)

                    driver.execute_script(f"window.scrollBy({height}, 200);")  # Scrolls down 500px
                    height += (height + (i * height))

                    # Scroll to pagination
                    page_next = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")

                    # isDisabled = False
                    if page_next:
                        ActionChains(driver) \
                            .scroll_to_element(page_next) \
                            .perform()
                        logger.info("Scroll to Next success")
                        # get all products in page
                        items = get_product(driver)
                        logger.info(f'{items}')

                        logger.info("Items collected Next button seen")
                        ActionChains(driver) \
                            .move_to_element(page_next) \
                            .click().perform()

                    # isDisabled = False
                    # next_end = WebDriverWait(driver, 10).until(
                    #     EC.presence_of_element_located(
                    #         (By.CSS_SELECTOR, "span.s-pagination-next")
                    #     )
                    # )
                    next_class = page_next.get_attribute('class')
                    logger.info(next_class)
                    if 'disabled' in next_class:
                        items = get_product(driver)
                        return items
                    elif page_visited == 6:
                        items = get_product(driver)
                        return items

                    logger.info("Next page button clicked")
                    # # Check if page 6 is visible (you can change this to any number)
                    # target_page = "6"
                    # try:
                    #     page = driver.find_element(By.CSS_SELECTOR, "span.s-pagination-selected").text
                    #     if page == target_page:
                    #         logger.info("Page 6 is found. Breaking loop.")
                    #         items = get_product(driver)
                    #         return items
                    # except:
                    #     pass
                except Exception as e:
                    logger.error(f'last {e}')


async def main_amazon(url, search_text):
    metadata = URLS.get(url)
    if not metadata:
        print("Invalid URL.")
        return

    # test_driver = webdriver.Chrome()
    # Get the version of the Chrome browser being used
    # chrome_version = test_driver.capabilities['browserVersion']
    # print(chrome_version)
    # test_driver.close()

    options = Options()
    # normal waits till entire page resources are downloaded
    options.page_load_strategy = 'normal'
    options.timeouts = {'script': 120000}
    # options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.42 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        logger.info("Page load complete")
        # search the loaded page
        search_page = search(metadata, driver, search_text)
        # scroll page results page
        amzn = scroll_page(driver)
        logger.info(amzn)
    except Exception as e:
        logger.error(e)
    finally:
        driver.implicitly_wait(30000)  # seconds
        driver.quit()


async def scrape_amazon_async(search_text):  # Rename to indicate async
    # Selenium operations are synchronous, so we run them in a separate thread
    return await main_amazon(AMAZON, search_text)
