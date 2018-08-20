import json
import hmac
import os
import dropbox
from datetime import datetime
from flask import Flask, Response, request, abort
from hashlib import sha256
from assets.cleaner import get_clean_data
from assets.database import SQLighterTransaction
from assets.loggers import logger
from assets.pd_getter import PrivatBankAPIWrapper

app = Flask(__name__)
del app.logger.handlers[:]
for hdlr in logger.handlers:
    app.logger.addHandler(hdlr)
dbx = dropbox.Dropbox(os.getenv("DROP_AUTHTOKEN"))


@app.route('/updateDay/<date>', methods=["POST"])
def update_day(date):
    """
    Update specific date
    :param date: "YYYY-mm-dd"
    :return: None
    """
    privat_data = privat_api.get_dates(datetime.strptime(date, "%Y-%m-%d"))
    db_trns.post_transactions(privat_data)
    return Response(status=200)


@app.route('/updateDates/<start_date>/<end_date>', methods=["POST"])
def update_dates(start_date, end_date):
    """
    Update specific date
    :param start_date: "YYYY-mm-dd"
    :param end_date: "YYYY-mm-dd"
    :return: None
    """
    privat_data = privat_api.get_dates(
        datetime.strptime(start_date, "%Y-%m-%d"),
        datetime.strptime(end_date, "%Y-%m-%d")
    )
    db_trns.post_transactions(privat_data)
    return Response(status=200)


@app.route('/getToday', methods=["GET"])
def get_today_data():
    """

    :return: list of tuples
             ["date", "type", ...]
    """
    privat_data = privat_api.get_today()
    response = get_clean_data(privat_data).to_records().tolist()
    return str(response)


@app.route('/getDay/<date>/<data_type>', methods=["GET"])
def get_day_data(date, data_type="clean"):
    """
    Get specific date
    :param data_type: "raw" or "clean" possible
    :param date: "YYYY-mm-dd"
    :return: list of tuples
             ["date", "type", ...]
    """
    response = db_trns.get_trans_on_dates(start_date=date, data_type=data_type)
    return str((len(response), [i[5] for i in response]))


@app.route('/getDates/<start_date>/<end_date>/<data_type>', methods=["GET"])
def get_dates_data(start_date, end_date, data_type="clean"):
    """
    Get specific date
    :param start_date: "YYYY-mm-dd"
    :param end_date: "YYYY-mm-dd"
    :param data_type: "raw" or "clean" possible
    :return: list of tuples
             ["date", "type", ...]
    """
    response = db_trns.get_trans_on_dates(start_date, end_date, data_type)
    return str((len(response), [i[5] for i in response]))


@app.after_request
def after_request(response):
    app.logger.info('%s %s %s %s %s',
                    request.remote_addr,
                    request.method,
                    request.scheme,
                    request.full_path,
                    response.status)
    return response


@app.route('/webhook', methods=['GET'])
def challenge():
    """Respond to the webhook challenge (GET request) by echoing back the challenge parameter."""

    resp = Response(request.args.get('challenge'))
    resp.headers['Content-Type'] = 'text/plain'
    resp.headers['X-Content-Type-Options'] = 'nosniff'

    return resp


@app.route('/webhook', methods=['POST'])
def webhook():

    for account in json.loads(request.data.decode("utf-8"))['list_folder']['accounts']:
        files = dbx.files_list_folder('/cache')
        files_diff = (max([file.server_modified for file in files.entries]) -
                      min([file.server_modified for file in files.entries])).total_seconds() / 60
        today_diff = (datetime.now() -
                      max([file.server_modified for file in files.entries])).total_seconds() / 60
        print(datetime.now(),
              max([file.server_modified for file in files.entries]))
        if files_diff < 2 and today_diff < 5:
            md, res = dbx.files_download("/cache/long.csv")
            print(res.content.eccode("utf-8"))
    return ""



if __name__ == '__main__':
    with open("configs.json", "r") as f:
        configs = json.load(f)

    privat_api = PrivatBankAPIWrapper(configs=configs)
    db_trns = SQLighterTransaction("./data/bot.db")

    app.run(debug=True, port=5005, host="0.0.0.0")
