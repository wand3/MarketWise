from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from amazon import get_product

AMAZON = "https://amazon.ca"
ALIEXPRESS = "https://aliexpress.com"

URLS = {
    AMAZON: {
        "search_field_query": 'input[name="field-keywords"]',
        "search_button_query": 'input[value="Go"]',
        "product_selector": "div.s-card-container"
    }
}

available_urls = URLS.keys()


def search(metadata, driver, search_text):
    logging.info(f"Searching for {search_text} on {driver.current_url}")

    search_field_query = metadata.get("search_field_query")
    search_button_query = metadata.get("search_button_query")

    if search_field_query and search_button_query:
        logging.info("Filling input field")

        # Wait for the search box to appear and type into it
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, search_field_query))
        )
        search_box.clear()
        search_box.send_keys(search_text)

        logging.info("Pressing search button")

        # Wait for the search button to appear and click it
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, search_button_query))
        )
        search_button.click()

        # Wait for the page to load (basic wait, can be customized)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    else:
        raise Exception("Could not search: missing selectors.")

    return driver


def get_products(driver, search_text, selector, get_product):
    print("Retrieving products.")
    product_divs = driver.find_elements(By.CSS_SELECTOR, selector)
    valid_products = []
    words = search_text.lower().split()

    for div in product_divs:
        product = get_product(div)  # get_product should be sync

        if not product.get("price") or not product.get("url"):
            continue

        name = product.get("name", "").lower()
        if all(word in name for word in words):
            valid_products.append(product)

    return valid_products


def main():
    # test_driver = webdriver.Chrome()
    # Get the version of the Chrome browser being used
    # chrome_version = test_driver.capabilities['browserVersion']
    # print(chrome_version)
    # test_driver.close()
    options = Options()
    # options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.42 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://google.com")
        driver.implicitly_wait(15)
    finally:
        driver.quit()

