import time
from argparse import ArgumentParser

import telebot
from assets.config import *
from assets.database import SQLighterUser
from assets.loggers import logger
from assets.models_bot import *
from flask import Flask, request

TOKEN = os.environ['BOT_TOKEN']

telebot.logger = logger
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

REQUES_DICT = {
    "amount": AmountService().amount,
    "date": DateService().parse,
}

temp_transactions = {}


@app.route('/' + TOKEN, methods=['POST'])
def process_updates():
    length = int(request.headers['content-length'])
    json_string = request.data.decode("utf-8")[:length]
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return


@bot.message_handler(commands=['transaction'])
def handle_transaction(message):
    u_id = int(message.chat.id)
    if validated_user_id(u_id):
        msg = bot.reply_to(
            message,
            """
            Транзакция была сегодня?
            """)
        bot.register_next_step_handler(msg, handle_transaction_date)


def handle_transaction_date(message):
    transaction = Transaction()
    try:
        u_id = message.chat.id
        if message.text.lower() != "да":
            transaction.time = DateService().parse(message.text)
        temp_transactions[u_id] = transaction

        msg = bot.reply_to(
            message,
            """
            Сколько потрачено?
            """)
        bot.register_next_step_handler(msg, handle_transaction_amount)
    except Exception as e:
        telebot.logger.error(e)
        bot.reply_to(message, 'Что-то не получилось!')


def handle_transaction_amount(message):
    try:
        u_id = message.chat.id
#        amount = AmountService().amount(message.text)[0]
        amount = re.findall("\d+", message.text)[0]
        if amount is None:
            msg = bot.reply_to(message, 'Не понял.')
            bot.register_next_step_handler(msg, handle_transaction_amount)
            return
        temp_transactions[u_id].amount = amount

        msg = bot.reply_to(
            message,
            """
            Где потратился?
            """)
        bot.register_next_step_handler(msg, handle_transaction_venue)

        # here should be markup with predicted venues
        # markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        # markup.add('Male', 'Female')
        # msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
        # bot.register_next_step_handler(msg, process_sex_step)

    except Exception as e:
        telebot.logger.error(e)
        bot.reply_to(message, 'Что-то не получилось!')


def handle_transaction_venue(message):
    try:
        u_id = message.chat.id
        # here also location, address, foursquare_id
        venue_name = message.venue.title
        temp_transactions[u_id].venue = venue_name

        t = temp_transactions[u_id]
        bot.send_message(u_id,
                         """
                         {} потачено {} в {}. 
                         """.format(str(t.time), t.amount, t.venue))
    except Exception as e:
        telebot.logger.error(e)
        bot.reply_to(message, 'Что-то не получилось!')


@app.errorhandler(500)
def internal_error(exception):
    app.error(exception)


def validated_user_id(u_id):
    db_worker = SQLighterUser(database_path="./data/bot.db")

    if int(u_id) not in db_worker.get_allowed_users():
        bot.send_message(
            u_id,
            """
            You are not allowed to use this system! Please contact @nikodrum for details.
            """)
        bot.send_message(
            db_worker.get_allowed_users(superuser=True)[0],
            """
            Alert!Alert!Alert!
            User {} tried to access the system.
            """.format(u_id))

        telebot.logger.warning("User {} tried to access system.".format(u_id))
        db_worker.close()
        return False
    db_worker.close()
    return True


def _setup(application):
    bot.set_webhook(url='https://%s:%s/%s' % (HOST, PORT, TOKEN),
                    certificate=open(CERT, 'rb'))
    del application.logger.handlers[:]
    for hdlr in logger.handlers:
        application.logger.addHandler(hdlr)

    return app


if __name__ == '__main__':

    arg_parser = ArgumentParser('Execution environment.')
    arg_parser.add_argument('-e',
                            '--envir',
                            required=True,
                            help='local/prod')
    args = arg_parser.parse_args()

    if args.envir == "production":
        HOST = WEBHOOK_LISTEN
        PORT = WEBHOOK_PORT
        CERT = WEBHOOK_SSL_CERT
        CERT_KEY = WEBHOOK_SSL_PRIV
        context = (CERT, CERT_KEY)

        app = _setup(app)
        time.sleep(2)

        app.run(host='0.0.0.0',
                port=PORT,
                ssl_context=context,
                debug=False)

    if args.envir == "local":
        class app:
            logger = logger

        bot.polling(none_stop=True)
