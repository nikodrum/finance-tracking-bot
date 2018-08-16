import sqlite3
import os
from datetime import datetime
from assets.config import DATA_SCHEMA, DATA_SCHEMA_CLEAN
from assets.cleaner import get_clean_data


def init_database(database_path):
    connection = sqlite3.connect(database_path)
    c = connection.cursor()

    c.execute(
        '''CREATE TABLE Users (
                user_id int NOT NULL PRIMARY KEY,
                inserted_date text,
                superuser int
        )''')

    c.execute(
        '''CREATE TABLE TransactionsRaw (
                transaction_id int NOT NULL PRIMARY KEY,
                pb_id, str,
                card int,
                appcode int,
                trandate str,
                trantime str,
                amount str,
                cardamount str,
                rest str,
                terminal str,
                description str
        )''')

    c.execute(
        '''CREATE TABLE Transactions (
                transaction_id int,
                inserted_on str,
                final_version int,
                category str,
                subcategory str,
                trandate str,
                trantime str,
                amount float,
                amount_currency str,
                cardamount float,
                store str,
                transaction_id_raw int,
                FOREIGN KEY (transaction_id) 
                    REFERENCES TransactionsRaw (transaction_id) 
                    ON UPDATE NO ACTION
        )''')

    c.execute(
        '''CREATE TABLE CategoryDict (
                text str,
                store str,
                category str,
                subcategory str
        )''')
    c.execute(
        'INSERT INTO users VALUES (?,?,?)', (str(datetime.now()), 163440579, True)
    ).fetchall()
    connection.commit()
    connection.close()


class SQLighterUser:
    def __init__(self, database_path):
        if os.path.exists(database_path):
            self.connection = sqlite3.connect(database_path)
        else:
            init_database(database_path=database_path)
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


class SQLighterTransaction:
    def __init__(self, database_path):
        if os.path.exists(database_path):
            self.connection = sqlite3.connect(database_path)
        else:
            init_database(database_path=database_path)
            self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()

    def get_t_id(self):
        """ Get latest t_id"""
        with self.connection:
            return self.cursor.execute(
                """
                SELECT MAX(transaction_id) FROM TransactionsRaw
                """).fetchall()[0][0]

    def post_transactions(self, tr):
        """ Post both clean and raw data."""
        tr = tr[DATA_SCHEMA].reset_index(drop=True)
        tr_clean = get_clean_data(tr)
        tr["@pd_id"] = tr["@card"].astype(str) + "_" + tr["@rest"].astype(str)
        for ind in tr.index.tolist():
            with self.connection:
                t_id = self.get_t_id + 1
                self.cursor.execute(
                    """
                    INSERT INTO TransactionsRaw
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (t_id, *(tr.loc[ind, ['pd_id'] + DATA_SCHEMA].values.tolist()))
                ).fetchall()
                self.cursor.execute(
                    """
                    INSERT INTO Transactions
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (t_id, datetime.now(), False, *(tr_clean.loc[ind, DATA_SCHEMA_CLEAN].values.tolist()))
                ).fetchall()
                self.connection.commit()

    def get_dates(self, start_date, end_date=None, data_type="clean"):

        table = "Transactions"
        if data_type == "raw":
            table = "TransactionsRaw"

        if end_date:
            with self.connection:
                return self.cursor.execute(
                    """
                    SELECT * FROM {}
                    WHERE trandate < ? 
                        AND trandate >= ?
                    """.format(table),
                    (end_date, start_date)
                ).fetchall()
        else:
            with self.connection:
                return self.cursor.execute(
                    """
                    SELECT * FROM {}
                    WHERE trandate = ?
                    """.format(table),
                    (start_date, )
                ).fetchall()
