from assets.database import SQLighterUser
from assets.config import *


def _setup(application):
    bot.set_webhook(url='https://%s:%s/%s' % (HOST, PORT, TOKEN),
                    certificate=open(CERT, 'rb'))
    del application.logger.handlers[:]
    for hdlr in logger.handlers:
        application.logger.addHandler(hdlr)

    return app


def validated_user_id(u_id):
    db_worker = SQLighterUser(database="bot.db")

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
