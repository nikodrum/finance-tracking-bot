import json
from datetime import datetime
from flask import Flask
from assets.pd_getter import PrivatBankAPIWrapper
from assets.database import SQLighterTransaction
app = Flask(__name__)


@app.route('/updateToday', method=["POST"])
def update_today_data():

    privat_data = privat_api.get_today()
    db_trns.post_transactions(privat_data)


@app.route('/getToday', method=["GET"])
def get_today_data():
    """

    :return: list of tuples
             ["date", "type", ...]
    """
    update_today_data()
    response = db_trns.get_dates(str(datetime.now().date()))
    return response


@app.route('/updateDay/<date>', method=["POST"])
def update_date(date):
    """
    Update specific date
    :param date: "YYYY-mm-dd"
    :return: None
    """
    privat_data = privat_api.get_dates(datetime.strptime(date, "%Y-%m-%d"))
    db_trns.post_transactions(privat_data)


@app.route('/getDate/<date>/<type>', method=["GET"])
def get_date_data(date, data_type="clean"):
    """
    Get specific date
    :param data_type: "raw" or "clean" possible
    :param date: "YYYY-mm-dd"
    :return: list of tuples
             ["date", "type", ...]
    """
    update_date(date)
    response = db_trns.get_dates(date, data_type)
    return response


if __name__ == '__main__':

    with open("configs.json", "r") as f:
        configs = json.load(f)

    privat_api = PrivatBankAPIWrapper(configs=configs)
    db_trns = SQLighterTransaction("./data/bot.db")

    app.run(debug=True, port=5005)
