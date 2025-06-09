import random
import time
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from logger import setup_logger


logger = setup_logger("aliexpress", "DEBUG", "scraper.log")
# uniform to mimic more human like randon with floats
delay = random.uniform(5, 15)


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
        logger.error(products)

    return products


# scroll to pagination part of page
def scroll_page_aliexpress(driver):
    logger.info("Scroll in")

    # Wait for the search button to appear and click it
    # dismiss_button = WebDriverWait(driver, 5).until(
    #     EC.element_to_be_clickable((By.CLASS_NAME, 'esm--upload-close--1x0SREz'))
    # )
    # logger.info("dismiss success")
    # dismiss_button = driver.find_element(By.CLASS_NAME, 'esm--upload-close--1x0SREz')
    # if dismiss_button:
    #     dismiss_button.click()
    #     logger.info("click success")
    # logger.info("Dismiss didn't pop up")
    scroll_count = 15
    height = 0

    for i in range(scroll_count):
        driver.execute_script(f"window.scrollBy({height}, 600);")  # Scrolls down 500px
        height += (height + (i * height))
        # Pause for a random time between 5 and 15 seconds
        time.sleep(3)
        # Scroll to pagination
        # go_to_page = driver.find_element(By.XPATH, "//div[contains(@class,'comet-pagination-options-quick-jumper')]")
        # go_to_page = driver.find_element(By.CSS_SELECTOR, "li.comet-pagination-next > button.comet-pagination-item-link")
        # go_to_page = driver.find_element(
        #     By.XPATH,
        #     "//li[contains(@class,'comet-pagination-next') and @aria-disabled='false']/button"
        # )

        try:
            go_to_page = driver.find_element(By.CLASS_NAME, "comet-pagination-item-link")

            if go_to_page:
                try:
                    items = get_product(driver)
                    logger.error(f"Items on Scroll {items}")
                    ActionChains(driver) \
                        .scroll_to_element(go_to_page) \
                        .perform()
                    logger.info("Scrolled to Go to page")
                    go_to_page.find_element(By.TAG_NAME, "button").click()



                    # # Wait for the input to appear and click it
                    # page_input_visible = WebDriverWait(driver, 10).until(
                    #     EC.element_to_be_clickable(
                    #         (By.CSS_SELECTOR, '.comet-pagination-options-quick-jumper input[type="text"]'))
                    # )
                    # logger.info("dismiss success")
                    #
                    # # fill page number
                    # if page_input_visible:
                    #     page_input = driver.find_element(By.CSS_SELECTOR,
                    #                                      '.comet-pagination-options-quick-jumper input[type="text"]')
                    #     ActionChains(driver) \
                    #         .scroll_to_element(page_input) \
                    #         .click() \
                    #         .send_keys('2') \
                    #         .perform()
                    #     logger.info("Type page number success")
                    # else:
                    #     logger.info("Type page number failed")

                    # Wait up to 15 seconds for the button to appear and become clickable
                    wait = WebDriverWait(driver, 15)
                    next_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.comet-pagination-item-link"))
                    )

                    # Click it
                    next_button.click()
                    logger.info("Next page button clicked")

                except Exception as e:
                    logger.error(f"Scroll again : {e}")
            # finally:
            #     footer = driver.find_element(By.CSS_SELECTOR, "site-footer")
            #     if footer:
            #         logger.info('Page end without pagination')
            #         return
        except Exception as e:
            logger.error(f"Scroll again : {e}")

        logger.info(f"Scrolled {i}")

