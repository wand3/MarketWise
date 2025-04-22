import random
import time
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from logger import logger


def get_stock(soup):
    # Find all divs with the specified class
    all_divs = soup.find_all("div", attrs={"class": "jt_j6"})
    logger.info(f"divs on scroll: {len(all_divs)}")

    return all_divs


def get_product(driver):
    # Get the page content
    html_code = driver.page_source
    # get all searched products on each page scroll
    soup = BeautifulSoup(html_code, 'html.parser')
    listitems = get_stock(soup)
    # logger.info(listitems)

    products = []
    product = {}
    for item in listitems:
        product_image = item.find("img", class_="mj_en")
        product_name = item.find("h3", class_="jt_kr")
        product_link = item.find("a", class_="search-card-item")
        product_price = item.find("div", class_="jt_kt")

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
        product["source"] = "Aliexpress"
        products.append(product)
        logger.info(product)

    return products


# scroll to pagination part of page
def scroll_page_aliexpress(driver):
    logger.info("Scroll in")

    # Wait for the search button to appear and click it
    dismiss_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'esm--upload-close--1x0SREz'))
    )
    logger.info("dismiss success")

    if dismiss_button:
        dismiss_button.click()
        logger.info("click success")

    # Scroll to pagination
    page_no = driver.find_element(By.CSS_SELECTOR, "comet-pagination-options-quick-jumper-button")
    ActionChains(driver)\
        .scroll_to_element(page_no)\
        .perform()
    logger.info("Next page button")
    logger.info("Scroll to bottom success")

    # next_page = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Next"))
    # )

    # next button
    # Wait for next button to be clickable
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.s-pagination-next")
        )
    )

    # Scroll into view and click
    if next_button:
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        next_button.click()
        logger.info("next page clicked")
        time.sleep(5)
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.PAGE_DOWN)  # or Keys.ARROW_DOWN, Keys.END, etc.    # if next_button:

    items = get_product(driver)

    # logger.info(items)

    # if next_page:
    #     ActionChains(driver) \
    #         .move_to_element(next_page) \
    #         .pause(5) \
    #         .click()

    logger.info("Next page button clicked")
    time.sleep(5)
    driver.implicitly_wait(random.randint(3, 6))  # seconds
    return items
