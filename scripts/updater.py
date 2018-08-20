import requests
import time
from assets.loggers import logger
from assets.config import SERVER_API
from assets.models_bot import send_notification
from datetime import datetime, timedelta
from pytz import timezone

KYIV = timezone("Europe/Kiev")


def run_script():
    while True:
        if datetime.now(tz=KYIV).time().hour == 0:
            day = (datetime.now(tz=KYIV) - timedelta(days=1)).date()
            logger.info("Automatic update of {}.".format(day))
            requests.post(SERVER_API + "/updateDay/{}".format(day))
            send_notification("Update successful for {}.".format(day))
        time.sleep(3600)

if __name__ == "__main__":
    logger.info("Automatic update script started.")
    run_script()
