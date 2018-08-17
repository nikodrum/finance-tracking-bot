import os
import re
import requests
import pytz
from datetime import datetime, timedelta, date
from assets.loggers import logger


def send_notification(message, user_id=163440579):
    response = requests.get(
        url="https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
            os.getenv("BOT_TOKEN"), user_id, message
        )
    )
    logger.info("Message status {}.".format(response.status_code))


class Transaction:
    def __init__(self,
                 amount=None,
                 venue=None,
                 category=None,
                 time=datetime.now().date()):
        self.amount = amount
        self.venue = venue
        self.category = category
        self.time = time


class DateService(object):
    __month__ = [
        "январь", "февраль",
        "март", "апрель", "май",
        "июнь", "июль", "август",
        "сентябрь", "октябрь", "ноябрь",
        "декабрь"
    ]

    __monthMod__ = [
        "января", "февраля",
        "марта", "апреля", "мая",
        "июня", "июля", "августа",
        "сентября", "октября", "ноября",
        "декабря"
    ]
    __relative__ = {
        "вчера": datetime.now(pytz.timezone('Europe/Kiev')) - timedelta(days=1),
        "позавчера": datetime.now(pytz.timezone('Europe/Kiev')) - timedelta(days=2)
    }
    __dayPattern__ = r"((\d{1,2})(го)?)|(вчера|позавчера)"

    def day(self, text):

        p_day = re.search(self.__dayPattern__, text)
        if p_day.group(4) is not None:
            return self.__relative__[p_day.group(4)].day
        if p_day.group(3) is not None:
            return int(p_day.group(2))

        _, month_name = self.month(text)
        if month_name is not None:
            possible_day = text.split(month_name)[0]
            return int(re.findall(r"\d{1,2}", possible_day)[0])

    def month(self, text):

        p_month = re.search(
            r"({})".format("|".join(self.__month__ + self.__monthMod__)), text
        )

        if p_month is not None:
            for i, m in enumerate(zip(self.__month__, self.__monthMod__)):
                p_month = re.search(r"({}|{})".format(m[0], m[1]), text)
                if p_month is not None:
                    return i + 1, p_month.group(1)

        return None, None

    def parse(self, text):
        day = self.day(text)
        if day is None:
            day = datetime.now(pytz.timezone('Europe/Kiev')).day
        month = self.month(text)[0]
        if month is None:
            month = datetime.now().month
        year = datetime.now().year
        return date(year, month, day)


class AmountService(object):
    __engCutCurr__ = [
        "uah", "usd", "eur"
    ]
    __rusCutCurr__ = [
        "грн", "дол", "евро"
    ]
    __engCurr__ = [
        "gryvnia", "dollar", "euro"
    ]
    __rusCurr__ = [
        "грив", "доллар", "евро"
    ]

    def amount(self, text):
        p_currency = None
        p_amount = None
        for i, currency in enumerate(self.__rusCutCurr__):
            p_amount = re.search(r"(\d+.?\d+)?\s?({}|{}|{}|{})".format(
                self.__engCurr__[i], self.__engCutCurr__[i],
                self.__rusCurr__[i], self.__rusCutCurr__[i]
            ), text)
            if p_amount.group(2) is not None:
                p_currency = self.__engCutCurr__[i]
                text = text.split(p_amount.group(2))[0]

        return p_amount, p_currency
