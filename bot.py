# импортируемые модули
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from urllib import request
import pytaf
import requests

# основные переменные
URL_METAR = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/UWUU.TXT"
URL_TAF = "https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/UWUU.TXT"
TOKEN = '1747286045:AAHRUwvGF2pM4lyZFjxJemL8hNdGGN-im-A'
reply_keyboard = [['/start', '/close'], ['/get_metar', '/get_taf']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"


# старт бота
def start(update, context):
    update.message.reply_text(
        "Это бот для получения авиационного прогноза погоды с серверов NOAA, адреса по локации или координатам\n"
        "Бот настроен на Уфимский аэропорт(UWUU)",
        reply_markup=markup
    )


# получение адреса по координатам
def get_address_from_coords(coords):
    parametres = {
        "apikey": apikey,
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }
    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=parametres)
        json_data = r.json()
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        return address_str
    except Exception as E:
        return 'Не могу определить адрес по этой локации или координатам, отправь мне запрос в правильном формате'


def close_keyboard(update, context):
    update.message.reply_text("Ok", reply_markup=ReplyKeyboardRemove())


# пользователь прислал любые координаты
def text(update, context):
    if update.message.text != "/close":
        coords = update.message.text
        address_str = get_address_from_coords(coords)
        update.message.reply_text(address_str)


# если пользователь отправил локацию с телефона
def location(update, context):
    message = update.message
    current_position = (message.location.longitude, message.location.latitude)
    coords = f"{current_position[0]},{current_position[1]}"
    address_str = get_address_from_coords(coords)
    update.message.reply_text(address_str)


# парсер с помощью pytaf
def parse_data(code):
    code = code.split('\n')[1]
    return pytaf.Decoder(pytaf.TAF(code)).decode_taf()


# METeorological Aerodrome Report
def get_metar(update, context):
    code = request.urlopen(URL_METAR).read().decode('utf-8')
    update.message.reply_text(parse_data(code), reply_markup=markup)


# TAF — Terminal Aerodrome Forecast
def get_taf(update, context):
    code = request.urlopen(URL_TAF).read().decode('utf-8')
    update.message.reply_text(parse_data(code), reply_markup=markup)


# главная функция
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("get_metar", get_metar))
    dp.add_handler(CommandHandler("get_taf", get_taf))
    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.location, location))
    updater.start_polling()
    updater.idle()


# Запуск бота
if __name__ == '__main__':
    main()
