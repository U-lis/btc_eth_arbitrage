import time
import datetime
from collections import OrderedDict, defaultdict, namedtuple

import requests
from lxml import html
import pytz
import telegram

KST = pytz.timezone("Asia/Seoul")

Spread = namedtuple("Spread", ["orig_market", "orig_price", "target_market", "target_price", "spread"])

URL = 'https://coinpan.com/files/currency/coinpan.html?ts={ts}'

TARGET_MARKET = ("빗썸", "코빗", "업비트", "코인원",)
TARGET_COIN = ("BTC", "BCH", "XRP", "ETH", "ETC", "QTUM")

CODE_MARKET = ("빗썸", "코빗", "업비트")
CODE_COIN = ("BTC", "BCH", "XRP")

TELEGRAM_TOKEN = "542001787:AAGwimVU0THJyejjMFpsAHeg0auL-jvApjQ"
THRESHOLD = 2

bot = telegram.Bot(TELEGRAM_TOKEN)
chat_id = -1001245127831


def crawl_data():
    """
    Crawl table data from coinpan.

    :return:
        {
            "[COIN_CODE]": [
                {"market_name": "price"},
                ...
            ],
            ...
        }
    """
    data = defaultdict(OrderedDict)
    ts = time.mktime(datetime.datetime.now(KST).timetuple())
    resp = requests.get(URL.format(ts=ts)).content.decode()
    tree = html.fromstring(resp)

    coin = None

    for ch in tree.iterchildren():
        if ch.tag == "dt":
            if ch.text in TARGET_COIN:
                coin = ch.text
            else:
                continue

        elif ch.tag == "dd":
            table = ch.getchildren()[-1]
            tbody = table.getchildren()[-1]
            for tr in tbody.iterchildren():
                market = tr.getchildren()[0].text.strip()
                if market not in TARGET_MARKET:
                    continue

                price = tr.getchildren()[1].text.strip()
                if price == "-":
                    continue

                price = int(price.replace("\\", "").replace(",", "").strip())
                if coin and price:
                    data[coin][market] = price
            coin = None

        else:
            continue
    print(data)
    return data


def make_code(data):
    """
    Make Code from crawled data.
    Calculate spread price of markets with following eq. and format.
    (BTC|BCH|XRP) { [bithumb|korbit|upbit] / coinone - 1 } [* 10000]    # 10000x for expensive coins.

    :param data: data from crawl_data()
    :return:
        "BTC 00/00/00 BCH 00/00/00 XRP 00/00/00"
    """
    result = []

    for coin_name in CODE_COIN:
        if coin_name not in data.keys():
            continue

        result.append(coin_name)
        if "코인원" not in data[coin_name] or data[coin_name]["코인원"] == "-":
            result.append(f"{coin_name} -/-/-")
        else:
            base = data[coin_name]["코인원"]
            code = []
            for target_market in CODE_MARKET:
                if target_market not in data[coin_name] or data[coin_name][target_market] == "-":
                    code.append("-")
                else:
                    code.append(str(round((data[coin_name][target_market] / base - 1)*10000)))
            result.append("/".join(code))
    full_code = " ".join(result)
    print(full_code)
    return full_code


def make_result(data):
    result = OrderedDict()

    for coin, info in data.items():
        while len(info) > 1:
            orig_market, orig_price = info.popitem(0)
            for target_market, target_price in info.items():
                spread = (target_price-orig_price) / orig_price * 100
                if abs(spread) >= THRESHOLD:
                    if coin not in result.keys():
                        result[coin] = []
                    result[coin].append(Spread(orig_market, orig_price, target_market, target_price, spread))
    print(result)
    return result


def make_report(code, result):
    message_list = [code+"\n"]

    for coin, rep in result.items():
        msg_list = [f"=== {coin} ==="]
        for r in rep:
            orig_price = f"{r.orig_price:,}" if r.orig_price < 1000000 else f"{r.orig_price//1000:,}K"
            target_price = f"{r.target_price:,}" if r.target_price < 1000000 else f"{r.target_price//1000:,}K"
            msg_list.append(f"{r.orig_market:>3} -> {r.target_market:>3} : {r.spread:.02f}% ({orig_price} -> {target_price})")
        message_list.append("\n".join(msg_list)+"\n")

    message = "\n".join(message_list)
    print(message)
    return message


def handler(event, context):
    crawled_data = crawl_data()
    full_code = make_code(crawled_data)
    result = make_result(crawled_data)
    message = make_report(full_code, result)
    bot.sendMessage(chat_id=chat_id, text=message)
    print("Message Sent.")
