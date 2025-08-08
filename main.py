import requests
import telebot
from datetime import datetime, timedelta
import os
import json
import time
import urllib3
import pytz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "7962129566:AAG3m-uW8ziyz8qvgtwaoDje-kOKgKRAfJM"
CHAT_ID = "@Money_in_Move"
MESSAGE_FILE = "message_id.json"

bot = telebot.TeleBot(TOKEN)

def safe_request(url, params=None, retries=3):
    """Безопасный запрос с повторными попытками"""
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, verify=False, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Попытка {attempt + 1}/{retries} не удалась: {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise e

def get_usd_rub():
    """Курс USD к RUB с ЦБ РФ"""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        return round(response.json()["Valute"]["USD"]["Value"], 2)
    except Exception as e:
        print(f"Ошибка при получении курса USD: {e}")
        return "N/A"

def get_btc_usd():
    """Курс Bitcoin к USD с улучшенной обработкой ошибок"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    
    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
            headers={'User-Agent': 'Mozilla/5.0'},
            verify=False
        )
        
        if response.status_code == 429:
            time.sleep(10)
            return get_btc_usd()
            
        response.raise_for_status()
        data = response.json()
        return round(data["bitcoin"]["usd"], 2)
        
    except requests.exceptions.SSLError:
        try:
            response = requests.get(url, params=params, timeout=15, verify=False)
            return round(response.json()["bitcoin"]["usd"], 2)
        except:
            return get_btc_usd_backup()
            
    except Exception as e:
        print(f"Ошибка CoinGecko: {e}")
        return get_btc_usd_backup()

def get_btc_usd_backup():
    """Резервные источники курса BTC"""
    sources = [
        {"url": "https://api.binance.com/api/v3/ticker/price", "params": {"symbol": "BTCUSDT"}, "key": "price"},
        {"url": "https://api.coinbase.com/v2/prices/BTC-USD/spot", "key": "data.amount"},
        {"url": "https://blockchain.info/ticker", "key": "USD.last"}
    ]
    
    for source in sources:
        try:
            response = requests.get(source["url"], params=source.get("params"), timeout=5)
            data = response.json()
            
            keys = source["key"].split('.')
            value = data
            for key in keys:
                value = value[key]
                
            return round(float(value), 2)
            
        except:
            continue
            
    return "N/A"

def get_imoex():
    """Индекс МосБиржи (IMOEX)"""
    url = "https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities/IMOEX.json"
    try:
        data = safe_request(url)
        return round(data["marketdata"]["data"][0][2], 2)
    except:
        return "N/A"

def format_value(value):
    """Форматирование значения с разделителями"""
    if value == "N/A":
        return value
    if isinstance(value, (int, float)):
        return f"{value:,.2f}".replace(",", " ")
    return str(value)

def build_message(force_update=False):
    """
    Создает сообщение с проверкой на необходимость обновления
    :param force_update: Если True, игнорирует проверку изменений
    :return: Кортеж (текст сообщения, флаг изменения данных)
    """
    usd = get_usd_rub()
    btc = get_btc_usd()
    imoex = get_imoex()
    now = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%H:%M")

    # Кэшируем предыдущие значения для сравнения
    prev_values = getattr(build_message, 'prev_values', {})
    has_changes = force_update or any([
        prev_values.get('usd') != usd,
        prev_values.get('btc') != btc,
        prev_values.get('imoex') != imoex
    ])
    
    build_message.prev_values = {
        'usd': usd,
        'btc': btc,
        'imoex': imoex
    }

    text = (
        f"🟢 USD   {format_value(usd)}₽\n"
        f"🟠 BTC   {format_value(btc)}$\n"
        f"🔴 IMOEX   {format_value(imoex)}₽\n"
        f"Обновлено сегодня в {now} _МСК_"
    )
    
    return text, has_changes


def update_message():
    if os.path.exists(MESSAGE_FILE):
        try:
            with open(MESSAGE_FILE, "r") as f:
                msg_data = json.load(f)
                msg_id = msg_data["message_id"]
                prev_text = msg_data.get("text", "")
            
            new_text, has_changes = build_message()
            
            if not has_changes and new_text == prev_text:
                print("Данные не изменились, пропускаем обновление")
                return True
                
            if new_text != prev_text:
                bot.edit_message_text(
                    chat_id=CHAT_ID,
                    message_id=msg_id,
                    text=new_text,
                    parse_mode="Markdown"
                )

                with open(MESSAGE_FILE, "w") as f:
                    json.dump({"message_id": msg_id, "text": new_text}, f)
                print("Сообщение успешно обновлено")
            
            return True
            
        except Exception as e:
            print(f"Ошибка при обновлении: {e}")
            os.remove(MESSAGE_FILE)
            return send_new_message()
    else:
        return send_new_message()


def send_new_message():
    """Отправляет новое сообщение и сохраняет его данные"""
    try:
        new_text, _ = build_message(force_update=True)
        msg = bot.send_message(
            chat_id=CHAT_ID,
            text=new_text,
            parse_mode="Markdown"
        )
        with open(MESSAGE_FILE, "w") as f:
            json.dump({
                "message_id": msg.message_id,
                "text": new_text
            }, f)
        print(f"Отправлено новое сообщение с ID: {msg.message_id}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке нового сообщения: {e}")
        return False

if __name__ == "__main__":
    update_message()