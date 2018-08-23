import json
import os
import dropbox
import traceback
from datetime import datetime
from flask import Flask, Response, request
from assets.cleaner import get_clean_pb_data
from database.wrappers import SQLighterTransaction
from assets.loggers import logger
from apis.privatbank import PrivatBankAPIWrapper
from apis.gmail import GmailAPIWrapper
from assets.models_bot import send_notification

app = Flask(__name__)
del app.logger.handlers[:]
for hdlr in logger.handlers:
    app.logger.addHandler(hdlr)


@app.route('/updateDay/<date>', methods=["POST"])
def update_day(date):
    """
    Update specific date
    :param date: "YYYY-mm-dd"
    :return: None
    """
    privat_data = privatbank.get_dates(datetime.strptime(date, "%Y-%m-%d"))
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
    privat_data = privatbank.get_dates(
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
    privat_data = privatbank.get_today()
    response = get_clean_pb_data(privat_data).to_records().tolist()
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


@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    logger.error('%s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                 request.remote_addr,
                 request.method,
                 request.scheme,
                 request.full_path,
                 tb)
    return "Internal Server Error", 500


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
        cache_files = dbx.files_list_folder('/cache').entries
        if len(cache_files) > 0:
            res = gmail.get_mono_trs()
            db_trns.post_transactions(
                tr=res,
                source="monobank"
            )
            send_notification("Done with monobank transactions.")
            for file in cache_files:
                dbx.files_delete_v2(file.path_display)
    return ""


if __name__ == '__main__':
    with open("./credentials/privatbank.json", "r") as f:
        configs = json.load(f)

    privatbank = PrivatBankAPIWrapper(configs=configs)
    gmail = GmailAPIWrapper()
    db_trns = SQLighterTransaction("./data/bot.db")
    dbx = dropbox.Dropbox(os.getenv("DROP_AUTHTOKEN"))

    app.run(debug=True, port=5005, host="0.0.0.0")
