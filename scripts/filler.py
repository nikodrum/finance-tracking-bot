import requests
import time
import random
from assets.loggers import logger
from assets.config import SERVER_API
from assets.models_bot import send_notification
from datetime import datetime, timedelta, date
from pytz import timezone

KYIV = timezone("Europe/Kiev")


def run_script():
    start_date = date(2016, 1, 1)

    while start_date < datetime.now().date():
        day = start_date
        requests.post(SERVER_API + "/updateDates/{}/{}".format(day, day + timedelta(days=3)))
        send_notification("Update successful for {} - {}.".format(day, day + timedelta(days=3)))
        start_date += timedelta(days=3)
        time.sleep(random.randint(50, 60)*random.randint(5, 10))


if __name__ == "__main__":
    logger.info("Automatic update script started.")
    run_script()
