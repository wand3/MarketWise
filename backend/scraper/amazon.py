import random
import time
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from logger import logger
import json
import os



def save_results(results):
    data = {"results": results}
    FILE = os.path.join("Scraper", "results.json")
    with open(FILE, "w") as f:
        json.dump([], f)
    with open(FILE, "r+") as contents:
        # load the existing data into a dict
        file_date = json.load(contents)
        # join new details (results) with file_date insinde emp_details
        file_date["emp_details"].append(results)
        # set files current posotion at offset
        contents.seek(0)

        # convert back to json
        json.dump(file_date, contents, indent=4)


def get_stock(soup):
    # Find all divs with the specified class
    all_divs = soup.find_all("div", attrs={"role": "listitem"})
    logger.info(f"divs on scroll: {len(all_divs)}")

    return all_divs


def get_product(driver):
    # Get the page content
    html_code = driver.page_source
    # get all searched products on each page scroll
    soup = BeautifulSoup(html_code, 'html.parser')
    listitems = get_stock(soup)
    # logger.info(listitems)

    product_name_element = ''
    product_price_element = ''
    product_link = ''

    # products = []
    product = {}
    for item in listitems:
        product_image = item.find("img", class_="s-image")
        product_name = item.find("h2", class_="a-size-medium")
        product_link = item.find("a", class_="a-link-normal")
        product_price = item.find("span", class_="a-offscreen")

        if product_name:
            name = product_name.text
            product["product_name"] = name
        if product_price:
            price = product_price.text
            product["product_price"] = price
        if product_image:
            href = product_image.get('src')
            product["image_url"] = href
        if product_link:
            href = product_link.get('href')
            product["product_url"] = "/".join(href.split("/")[:4])
        product["source"] = "Amazon"
        # products.append(product)
        logger.info(product)
        save_results({product})
    # return products


# scroll to pagination part of page
def scroll_page(driver):
    logger.info("Scroll in")

    # Wait for the search button to appear and click it
    dismiss_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@data-action-type="DISMISS"]'))
    )
    logger.info("dismiss success")

    if dismiss_button:
        dismiss_button.click()
        logger.info("click dismiss success")

    # Wait for next button to be clickable
    pages = 0
    while pages < 2:
        try:
            # Scroll to pagination
            page_no = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
            ActionChains(driver) \
                .scroll_to_element(page_no) \
                .perform()
            logger.info("Scroll to Next success")

            # isDisabled = False
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.s-pagination-next")
                )
            )
            # items = get_product(driver)
            # logger.info(items)

            if next_button:
                logger.info("Next button seen")
                ActionChains(driver) \
                    .move_to_element(next_button) \
                    .click().perform()

            
            # isDisabled = False
            next_end = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.s-pagination-next")
                )
            )
            next_class = next_end.get_attribute('class')
            logger.info(next_class)

            if 'disabled' in next_class:
                # isDisabled = True
                break
           
            logger.info("Next page button clicked")
            pages += 1
        except Exception as e:
            logger.error(e)
