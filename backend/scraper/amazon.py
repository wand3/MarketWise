import random
import time
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from logger import logger
from asyncio import gather


def get_stock(driver):
    # Get the page content
    html_code = driver.page_source

    # get all searched products on each page scroll
    soup = BeautifulSoup(html_code, 'html.parser')

    # Find all divs with the specified class
    all_divs = soup.find_all("div", attrs={"role": "listitem"})
    logger.info(f"divs on scroll: {len(all_divs)}")

    return all_divs


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
        logger.info("click success")

    # Scroll to pagination
    page_no = driver.find_element(By.PARTIAL_LINK_TEXT, "Next")
    ActionChains(driver)\
        .scroll_to_element(page_no)\
        .perform()
    logger.info("Next page button")

    next_page = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Next"))
    )
    # get all items using bs4
    items = get_stock(driver)
    logger.info(items)

    if next_page:
        ActionChains(driver) \
            .move_to_element(next_page) \
            .pause(5) \
            .click()

        logger.info("Next page button clicked")
        time.sleep(5)
        driver.implicitly_wait(random.randint(3, 6))  # seconds

    logger.info("Scroll to bottom success")



#     elements = await product_div.query_selector_all('.a-size-base')
#     filtered_elements = [element for element in elements if 'stock' in await element.inner_text()]
#     return filtered_elements


async def get_product(product_div):
    # Query for all elements at once
    image_element_future = product_div.query_selector('img.s-image')
    name_element_future = product_div.query_selector(
        'h2 a span')
    price_element_future = product_div.query_selector('span.a-offscreen')
    url_element_future = product_div.query_selector(
        'a.a-link-normal.s-no-hover.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')

    # Await all queries at once
    image_element, name_element, price_element, url_element = await gather(
        image_element_future,
        name_element_future,
        price_element_future,
        url_element_future,
        # get_stock(product_div)
    )

    # Fetch all attributes and text at once
    image_url = await image_element.get_attribute('src') if image_element else None
    product_name = await name_element.inner_text() if name_element else None
    try:
        print((await price_element.inner_text()).replace("$", "").replace(",", "").strip())
        product_price = float((await price_element.inner_text()).replace("$", "").replace(",", "").strip()) if price_element else None
    except:
        product_price = None
    product_url = "/".join((await url_element.get_attribute('href')).split("/")[:4]) if url_element else None
    # stock = stock_element[0] if len(stock_element) > 0 else None

    return {"img": image_url, "name": product_name, "price": product_price, "url": product_url}
