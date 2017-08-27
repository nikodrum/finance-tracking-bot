import sqlite3
import os
from datetime import datetime


def init_database(name):
    connection = sqlite3.connect("./data/{}.db".format(name))
    c = connection.cursor()

    c.execute(
        '''CREATE TABLE users (
                inserted_date text,
                user_id int,
                superuser int
        )''')

    connection.commit()
    connection.close()


class SQLighter:
    def __init__(self, database):
        database_path = "./data/{}".format(database)
        if os.path.exists(database_path):
            self.connection = sqlite3.connect(database_path)
        else:
            init_database(name="bot")
            self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()

    def select_all_users(self):
        """ Getting all users """
        with self.connection:
            return self.cursor.execute('SELECT * FROM users').fetchall()

    def get_allowed_users(self, superuser=False):
        """ 
        Getting users allowed to use system. 
            superuser = True - my id will be taken
        """
        with self.connection:
            if superuser:
                return self.cursor.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE superuser={}
                    """.format(int(superuser))
                ).fetchall()
            return [u[1] for u in self.select_all_users()]

    def check_user(self, u_id):
        """ Check user by user_id """
        with self.connection:
            return 1 == len(self.cursor.execute(
                'SELECT * FROM users WHERE user_id = ?', (u_id,)
            ).fetchall())

    def post_user(self, u_id):
        """ Put user. """
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users VALUES (?,?,?)', (str(datetime.now()), u_id, False)
            ).fetchall()
            self.connection.commit()

    def close(self):
        """ Close connection with DB """
        self.connection.close()
