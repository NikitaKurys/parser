from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


market_buttons = [
    [types.KeyboardButton(text='Wilberries')],
    [types.KeyboardButton(text='Ozon')],
    [types.KeyboardButton(text='Sbermarket')],
    [types.KeyboardButton(text='Все три маркета')]
]
market_kb = ReplyKeyboardMarkup(
    keyboard=market_buttons,
    resize_keyboard=True,
    input_field_placeholder="Выберите маркет"
)

filter_buttons = [
    [types.KeyboardButton(text='I - По популярности')],
    [types.KeyboardButton(text='II - Топ рейтинг')],
    [types.KeyboardButton(text='III - Сначало дешёвые')],
]
filter_kb = ReplyKeyboardMarkup(
    keyboard=filter_buttons,
    resize_keyboard=True,
    input_field_placeholder="Как будем сортировать?"
)

main_buttons = [
    [types.KeyboardButton(text='1 - Выбрать другую сортировку')],
    [types.KeyboardButton(text='2 - Выбрать другой маркет')],
    [types.KeyboardButton(text='3 - Выбрать другой продукт')],
    [types.KeyboardButton(text='4 - Закончить поиск')],
]
main_kb = ReplyKeyboardMarkup(
    keyboard=main_buttons,
    resize_keyboard=True,
    input_field_placeholder="Какие дальнейшие действия?"
)
