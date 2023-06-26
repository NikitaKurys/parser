import lxml

from asyncio import sleep
from settings import WB_URL
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import undetected_chromedriver

product_info = []


async def create_soup(html):
    soup = BeautifulSoup(html, 'lxml')
    product_names = soup.find_all('img', class_='j-thumbnail thumbnail')
    product_prices = soup.find_all(class_='price__lower-price')
    product_images = soup.find_all('img', class_='j-thumbnail thumbnail')
    product_rating = soup.find_all('span', class_='product-card__count')
    product_url = soup.find_all('a', class_='product-card__main j-card-link')
    for name, price, image, url, rating in zip(product_names[:3], product_prices[:3],
                                               product_images[:3], product_url[:3],
                                               product_rating[:3]):
        product_info.append([
                             {'Name': name.get('alt')},
                             {'Price': price.text.replace(u'\xa0', u'').strip()},
                             {'Image': 'https:' + image.get('src')},
                             {'Url': url.get('href')},
                             {'Rating': rating.text.replace('&nbsp;', '')},
                             ])


async def wb_parser(product: str, category, url=WB_URL):
    options = undetected_chromedriver.ChromeOptions()
    options.add_argument("--headless")
    driver = undetected_chromedriver.Chrome(options=options)
    driver.set_window_size(1000, 900)
    driver.get(url)
    await sleep(2)
    driver.find_element(By.XPATH, '/html/body/div[1]/header/div/div[2]/div[1]/div/button[3]').click()
    await sleep(1)
    driver.find_element(By.XPATH, '//*[@id="mobileSearchInput"]').send_keys(product + Keys.ENTER)
    await sleep(2)

    # Popular
    if category == 'I':
        await create_soup(driver.page_source)

    # Rating
    elif category == 'II':
        driver.find_element(By.CLASS_NAME, 'sorter-mobile__btn').click()
        await sleep(2)
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/ul/li[2]').click()
        await sleep(2)
        await create_soup(driver.page_source)

    # Min Price
    elif category == 'III':
        driver.find_element(By.CLASS_NAME, 'sorter-mobile__btn').click()
        await sleep(2)
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/ul/li[3]').click()
        await sleep(2)
        await create_soup(driver.page_source)
