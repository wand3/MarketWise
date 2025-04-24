import json
import os
import random
from logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from amazon import scroll_page
from aliexpress import get_stock, scroll_page_aliexpress

AMAZON = "https://amazon.com"
ALIEXPRESS = "https://aliexpress.com"

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


def main(url, search_text):
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
        if AMAZON:
            amzn = scroll_page(driver)
            # save_results(amzn)
        else:
            ali = scroll_page_aliexpress(driver)
            # save_results(ali)

    finally:
        driver.implicitly_wait(30000)  # seconds
        driver.quit()


if __name__ == "__main__":
    # test script
    main(AMAZON, "ryzen 9 3950x")
    # main(ALIEXPRESS, "ryzen 9 3950x")
