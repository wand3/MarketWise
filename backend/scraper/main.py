import json
import os
import random
from logger import setup_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from amazon import main_amazon
from aliexpress import get_stock, scroll_page_aliexpress


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



# def main(url, search_text):
#     metadata = URLS.get(url)
#     if not metadata:
#         print("Invalid URL.")
#         return
#
#     # test_driver = webdriver.Chrome()
#     # Get the version of the Chrome browser being used
#     # chrome_version = test_driver.capabilities['browserVersion']
#     # print(chrome_version)
#     # test_driver.close()
#
#     options = Options()
#     # normal waits till entire page resources are downloaded
#     options.page_load_strategy = 'normal'
#     options.timeouts = {'script': 120000}
#     # options.add_argument("--headless")
#     options.add_argument(
#         "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.42 Safari/537.36")
#     driver = webdriver.Chrome(options=options)
#     try:
#         driver.get(url)
#         logger.info("Page load complete")
#         # search the loaded page
#         search_page = search(metadata, driver, search_text)
#         # scroll page results page
#         if url == 'AMAZON':
#             amzn = scroll_page(driver)
#             logger.info(amzn)
#
#             # save_results(amzn)
#         else:
#             ali = scroll_page_aliexpress(driver)
#             # save_results(ali)
#     finally:
#         driver.implicitly_wait(30000)  # seconds
#         driver.quit()


def run_scrapers_async():
    data = main_amazon(AMAZON, 'ryback')


if __name__ == "__main__":
    main_amazon(AMAZON, 'ryback')
   # run_scrapers_async()
