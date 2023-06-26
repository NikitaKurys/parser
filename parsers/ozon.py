import lxml

from asyncio import sleep
from settings import OZON_URL
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import undetected_chromedriver

product_info = []


async def create_soup(html):
    soup = BeautifulSoup(html, 'lxml')
    # В озоне есть два типа карточек, проверяем какой из типов выбрал пользователь
    if len(soup.find_all('span', class_='_32-a3 _32-a5 _32-b')) != 0:
        product_names = soup.find_all('span', class_='e2g g2e e3g e5g tsBodyL w5k')
        product_prices = soup.find_all('span', class_='_32-a3 _32-a5 _32-b')
        product_images = soup.find_all('div', class_='xk1')
        product_url = soup.find_all('a', class_='tile-hover-target w5k')
        product_rating = soup.find_all('div', class_='dy8 d8y yd8 tsBodyMBold')
    else:
        product_names = soup.find_all('span', class_='e2g g2e e3g e5g tsBodyL w5k')
        product_prices = soup.find_all('span', class_='_32-a3 _32-a7')
        product_images = soup.find_all('div', class_='xk1 kx2')
        product_url = soup.find_all('a', class_='tile-hover-target w5k')
        product_rating = soup.find_all('div', class_='dy8 d8y yd8 tsBodyMBold')

    for name, price, image, url, rating in zip(product_names[:3], product_prices[:3],
                                               product_images[:3], product_url[:3],
                                               product_rating[:3]):

        product_info.append([
                             {'Name': name.text},
                             {'Price': price.find_next(class_='_32-a2').text.replace('&thinsp;', '')},
                             {'Image': image.find_next(class_='_24-a').get('src')},
                             {'Url': 'https://ozon.ru' + url.get('href')},
                             {'Rating': rating.text.split()[1]}
                             ])


async def ozon_parser(product: str, category, url=OZON_URL):
    options = undetected_chromedriver.ChromeOptions()
    options.add_argument("--headless")
    driver = undetected_chromedriver.Chrome(options=options)
    driver.set_window_size(880, 1200)
    driver.get(url)
    await sleep(2)
    driver.find_element(By.XPATH, '//*[@id="stickyHeader"]/div[3]/div/div/form/div[1]/div[2]/input[1]').send_keys(product)
    await sleep(1)
    driver.find_element(By.XPATH, '//*[@id="stickyHeader"]/div[3]/div/div[1]/form/div[2]/div/button/span').click()
    await sleep(2)

    # Popular
    if category == 'I':
        await sleep(3)
        await create_soup(driver.page_source)

    # Rating
    elif category == 'II':
        await sleep(2)
        new_url = driver.current_url.replace('&text', '&sorting=rating&text')
        driver.get(new_url)
        await create_soup(driver.page_source)

    # Min price
    elif category == 'III':
        await sleep(2)
        new_url = driver.current_url.replace('&text', '&sorting=ozon_card_price&text')
        driver.get(new_url)
        await create_soup(driver.page_source)
