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
from .logger import setup_logger
import json


logger = setup_logger("aliexpress", "DEBUG", "scraper.log")
# uniform to mimic more human like randon with floats
delay = random.uniform(3, 6)

ALIEXPRESS = "https://aliexpress.com"
URLS = {
    ALIEXPRESS: {
        "search_field_query": 'input[id="search-words"]',
        "search_button_query": 'input[type="button"]',
        "product_selector": ""
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
    all_divs = soup.find_all("div", attrs={"class": "hs_bu search-item-card-wrapper-gallery"})
    # logger.info(f"divs on scroll: {len(all_divs)}")
    return all_divs


def hash_product(product):
    """Create unique hash for product based on its URL and name"""
    return hashlib.md5(
        (product["product_url"] + product["product_name"]).encode()
    ).hexdigest()


def get_product(driver):
    # Get the page content
    html_code = driver.page_source
    # get all searched products on each page scroll
    soup = BeautifulSoup(html_code, 'html.parser')
    listitems = get_stock(soup)

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
    try:

        # Process current page items
        for item in listitems:
            product_image = item.find_all("img", class_="mn_bc")
            product_name = item.find("h3", class_="kr_j0")
            product_link = item.find("a", class_="search-card-item")
            product_price = item.find("div", class_="kr_kj")

            product = {
                "product_name": product_name.text if product_name else "N/A",
                "product_price": product_price.text if product_price else "N/A",
                "image_url": product_image[0].get('src') if product_image else "N/A",
                "product_url": "/".join(product_link.get('href').split('/')[:5]) if product_link else "N/A",
                "source": "Aliexpress"
            }

            logger.info(f'New product added: {product}')

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
        return current_page_products
    except Exception as e:
        return e


# scroll to pagination part of page
def scroll_page_aliexpress(driver):
    logger.info("Scroll in")
    page_visited = 0
    while True:
        try:
            # Wait for the dismiss button to appear and click it
            dismiss_button = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'esm--upload-close--1x0SREz'))
            )
            logger.info("dismiss success")
            dismiss_button = driver.find_element(By.CLASS_NAME, 'esm--upload-close--1x0SREz')
            if dismiss_button:
                dismiss_button.click()
                logger.info("click success")
        except Exception as e:
            logger.info(f"Dismiss didn't pop up {e}")

        scroll_count = 15
        height = 0

        scroll_pause_time = 2  # Pause between scrolls
        scroll_increment = 500  # Pixels to scroll each time
        max_scrolls = 10  # Maximum number of scrolls
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(max_scrolls):

        # for i in range(scroll_count):
            try:
                time.sleep(delay)
                # driver.execute_script(f"window.scrollBy(0, {100 * height});")  # Scrolls down 500px
                # height += (height + (i * 100))

                # Scroll down by increment
                driver.execute_script(f"window.scrollBy(0, {scroll_increment});")

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")

                # Break loop if we've reached the bottom
                if new_height == last_height:
                    break

                last_height = new_height
                # Scroll to pagination
                # go_to_page = driver.find_element(By.CLASS_NAME, ".comet-pagination")
                # # go_to_page = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div[3]")
                # logger.info("Go to page found")
                #
                # if go_to_page:
                #     try:
                #         ActionChains(driver) \
                #             .scroll_to_element(go_to_page) \
                #             .perform()
                #         logger.info("Scrolled to Go to page")
                #         next_page = driver.find_element(By.CSS_SELECTOR, ".comet-pagination-next")
                #         items = get_product(driver)
                #         logger.info(f"Items on Scroll {len(items)}")
                #         # logger.info(next_page.get_attribute("aria-disabled"))
                #         if next_page.get_attribute("aria-disabled") == 'false':
                #             logger.info(f"Active next page button seen")
                #             ActionChains(driver) \
                #                 .scroll_to_element(next_page) \
                #                 .click()
                #             next_page.click()
                #
                #             logger.info(f"Active next page button clicked")
                #             page_visited += 1
                #             time.sleep(delay)
                #             # next_page.click()
                #             if page_visited == 6:
                #                 # to stop page visits on page 6
                #                 # items = get_product(driver)
                #                 return items
                #
                #     except Exception as e:
                #         logger.error(f"Scroll again : {e}")
                # try:
                #     # Locate the whole pagination container
                #     pagination = driver.find_element(By.CSS_SELECTOR, "div.g7_ba ul.comet-pagination")
                #
                #     # Extract all page buttons (li elements that contain <button> or <a>)
                #     buttons = pagination.find_elements(By.CSS_SELECTOR, "li")
                #
                #     for btn in buttons:
                #         try:
                #             element = btn.find_element(By.CSS_SELECTOR, "button, a")  # either button or link
                #             text = element.text or btn.get_attribute("class")  # use text or class if empty
                #             location = element.location  # x,y coordinates
                #             size = element.size  # width,height
                #             # print(f"Button: {text} | Location: {location} | Size: {size}")
                #
                #             # find next button and click
                #             try:
                #                 next_li = driver.find_element(By.CSS_SELECTOR, "li.comet-pagination-next")
                #                 if next_li.get_attribute("aria-disabled") == "false":
                #                     items = get_product(driver)
                #                     logger.info(f"Items on Scroll {len(items)}")
                #
                #                     next_btn = next_li.find_element(By.TAG_NAME, "button")
                #                     next_btn.click()
                #                     print("✅ Moved to next page")
                #                 else:
                #                     print("⚠️ Next button is disabled (already on last page)")
                #             except Exception as e:
                #                 print("❌ Could not find Next button:", e)
                #
                #         except Exception as e:
                #             logger.error(f"Before Pagination find fail : {e}")
                #
                # except Exception as e:
                #
                #     logger.error(f"Pagination find fail : {e}")

            except Exception as e:
                logger.error(f"Exception : {e}")


async def main_aliexpress(url, search_text):
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
        alexp = scroll_page_aliexpress(driver)
        logger.info(alexp)
        if alexp:
            return True
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()


async def scrape_aliexpress_async(search_text):  # Rename to indicate async
    # Selenium operations are synchronous, so we run them in a separate thread
    return await main_aliexpress(ALIEXPRESS, search_text)
