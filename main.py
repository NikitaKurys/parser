from logger import logger

from parsers import ozon, sbermarket, wildberries
from parsers.ozon import ozon_parser
from parsers.wildberries import wb_parser
from parsers.sbermarket import sb_parser
from settings import TLG_TOKEN

from keyboards import market_kb, filter_kb, main_kb
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils.markdown import hlink
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

storage = MemoryStorage()
bot = Bot(token=TLG_TOKEN)
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    product = State()
    market = State()
    category = State()
    navigator = State()


# Вывод данных пользователю и логгирование сообщения
async def product_converter(any_parser, data, product_info: list,
                            title: str, msg: types.Message):
    await any_parser(data['product'], data['category'].split()[0])
    await msg.answer(f'Вот что я нашёл в {title} по слову {data["product"]}')

    if len(product_info) == 0:
        await msg.answer('Ой, что-то случилось, '
                         'попробуйте другой продукт или маркет')
        logger.info(f'Пользователь {msg.from_user.first_name} '
                    f'получил ошибку о недоступности маркета')

    else:
        for product in product_info:
            await bot.send_photo(chat_id=msg.chat.id,
                                 photo=product[2]["Image"],
                                 caption=(f'{product[0]["Name"]}\n'
                                          f'Цена: {product[1]["Price"]}\n'
                                          f'{product[4]["Rating"]} отзывов\n'))
            await bot.send_message(chat_id=msg.chat.id,
                                   text=hlink('Ссылка', product[3]['Url']),
                                   parse_mode="HTML",
                                   disable_web_page_preview=True)
        logger.info(f'Пользователь {msg.from_user.first_name} получил'
                    f'информацию о {len(product_info)} продуктах по запросу '
                    f'{data["product"], data["market"], data["category"]}')

    await msg.answer('Что будем делать далее?', reply_markup=main_kb)
    await UserState.next()
    product_info.clear()


@dp.message_handler(lambda msg: msg.text != '/start')
async def on_startup(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           f'Здравствуйте, {msg.from_user.first_name},'
                           f'MarketParserBot предназначен для поиска товаров'
                           f'в нескольких онлайн магазинах, чтоб попробовать'
                           f'бота в действии нажмите на "/start"')


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(msg: types.Message):
    await msg.answer('Укажите продукт')
    await UserState.product.set()


@dp.message_handler(state=UserState.product)
async def get_product(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['product'] = msg.text
    await msg.answer("Отлично! теперь укажите маркет",
                     reply_markup=market_kb)
    await UserState.next()


@dp.message_handler(state=UserState.market)
async def get_market(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['market'] = msg.text
    await msg.answer("Хороший выбор, теперь укажите как будем сортировать",
                     reply_markup=filter_kb)
    await UserState.next()


@dp.message_handler(state=UserState.category)
async def get_parser(msg: types.Message, state: FSMContext):
    await msg.answer("Подождите пару минут, ищу данные")
    async with state.proxy() as data:
        data['category'] = msg.text
    if data['market'] == 'Wilberries':
        await product_converter(wb_parser, data,
                                wildberries.product_info, 'Wilberries', msg)

    elif data['market'] == 'Ozon':
        await product_converter(ozon_parser, data,
                                ozon.product_info, 'Ozon', msg)

    elif data['market'] == 'Sbermarket':
        await product_converter(sb_parser, data,
                                sbermarket.product_info, 'Sbermarket', msg)

    elif data['market'] == 'Все три маркета':
        await product_converter(wb_parser, data,
                                wildberries.product_info, 'Wilberries', msg)
        await product_converter(ozon_parser, data,
                                ozon.product_info, 'Ozon', msg)
        await product_converter(sb_parser, data,
                                sbermarket.product_info, 'Sbermarket', msg)

    else:
        await msg.answer('К сожалению, я не знаю такой маркет')
        logger.info(f'Пользователь {msg.from_user.first_name} '
                    f'получил "Не известный маркет"')


# Навигатор состояний
@dp.message_handler(state=UserState.navigator)
async def get_navigator(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['navigator'] = msg.text.split()[0]
    logger.info(f'Пользователь {msg.from_user.first_name} выбрал {msg.text}')
    if data['navigator'] == '1':
        await state.set_state(UserState.category)
        await msg.answer('Укажите способ сортировки', reply_markup=filter_kb)

    elif data['navigator'] == '2':
        await state.set_state(UserState.market)
        await msg.answer('Укажите маркет', reply_markup=market_kb)

    elif data['navigator'] == '3':
        await state.set_state(UserState.product)
        await msg.answer('Укажите продукт')

    elif data['navigator'] == '4':
        await msg.answer('Всего хорошего, '
                         'для начала нового поиска нажмите на "/start"',
                         reply_markup=types.ReplyKeyboardRemove())
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp)
