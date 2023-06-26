import time
import lxml

from asyncio import sleep
import undetected_chromedriver
from settings import SBER_URL
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

product_info = []


async def create_soup(html):
    soup = BeautifulSoup(html, 'lxml')
    product_names = soup.find_all('div', class_='catalog-item-photo')
    product_prices = soup.find_all('div', class_='item-price')
    product_images = soup.find_all('div', class_='catalog-item-photo')
    product_url = soup.find_all('div', class_='item-title')
    product_rating = soup.find_all('div', class_='review-amount')

    for name, price, image, url, rating in zip(product_names[:3], product_prices[:3],
                                               product_images[:3], product_url[:3],
                                               product_rating[:3]):
        product_info.append([{'Name': name.find_next('img', class_='lazy-img').get('alt')},
                             {'Price': price.text.replace(u'\xa0', u'')},
                             {'Image': image.find_next('img', class_='lazy-img').get('src')},
                             {'Url': SBER_URL + url.find_next('a', class_='ddl_product_link').get('href')},
                             {'Rating': rating.text}])


async def sb_parser(product: str, category, url=SBER_URL):
    options = undetected_chromedriver.ChromeOptions()
    options.add_argument("--headless")
    driver = undetected_chromedriver.Chrome(options=options)
    driver.get(url)
    await sleep(2)
    driver.find_element(By.CLASS_NAME, 'search-field-input').send_keys(product + Keys.ENTER)
    await sleep(1)

    # Popular
    if category == 'I':
        await sleep(2)
        await create_soup(driver.page_source)

    # Rating
    elif category == 'II':
        if 'related_search' in driver.current_url:
            new_url = driver.current_url + '&sort=3'
            driver.get(new_url)
            await sleep(1)
            await create_soup(driver.page_source)
        else:
            new_url = driver.current_url + '#?sort=3'
            driver.get(new_url)
            await sleep(2)
            await create_soup(driver.page_source)

    # Min price
    elif category == 'III':
        if 'related_search' in driver.current_url:
            new_url = driver.current_url + '&sort=1'
            driver.get(new_url)
            await sleep(1)
            await create_soup(driver.page_source)
        else:
            new_url = driver.current_url + '#?sort=1'
            driver.get(new_url)
            await sleep(2)
            await create_soup(driver.page_source)

