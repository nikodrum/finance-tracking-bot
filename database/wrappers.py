import sqlite3
import os
from datetime import datetime
from assets.loggers import logger
from assets.cleaner import *
from database.config import db_init


class SQLighterUser:
    def __init__(self, database_path):
        if os.path.exists(database_path):
            self.connection = sqlite3.connect(database_path, check_same_thread=False)
        else:
            db_init(database_path=database_path)
            self.connection = sqlite3.connect(database_path, check_same_thread=False)
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
            self.connection = sqlite3.connect(database_path, check_same_thread=False)
        else:
            db_init(database_path=database_path)
            self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_t_id(self, table):
        """ Get latest t_id"""
        with self.connection:
            t_id = self.cursor.execute(
                """
                SELECT MAX(transaction_id) FROM {}
                """.format(table)).fetchall()[0][0]
            if t_id:
                return t_id + 1
            return 1

    def existing_transaction(self, pb_id):
        """ Check whether transaction is in the database. In use pb_id field. """
        with self.connection:
            return 1 == self.cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM TransactionsRaw
                        WHERE pb_id = (?) LIMIT 1)
                    """, (pb_id,)
            ).fetchall()[0][0]

    def post_transactions(self, tr, source="privatbank"):
        """ Post both clean and raw data."""
        if source == "monobank":
            self._post_monobank(tr)
        if source == "privatbank":
            self._post_privatbank(tr)

    def _post_monobank(self, tr):
        tr = get_raw_mono_data(tr)
        tr_clean = get_clean_mono_data(tr)
        tr["@pb_id"] = tr.apply(
            lambda r: (str(r.loc["@card"])[-4:] + "|" +
                       str(r.loc["@rest"]) + "|" +
                       str(r.loc["@trandate"])),
            axis=1)
        c = 0
        for ind in tr.index.tolist():
            with self.connection:
                t_id = self.get_t_id("TransactionsRaw")

                if not self.existing_transaction(tr.loc[ind, "@pb_id"]):
                    self.cursor.execute(
                        """
                        INSERT INTO TransactionsRaw VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """, (t_id, *(tr.loc[ind, ['@pb_id'] + DATA_SCHEMA].values.tolist()))
                    ).fetchall()
                    if ind in tr_clean.index.tolist():
                        self.cursor.execute(
                            """
                            INSERT INTO Transactions VALUES (?,?,?,?,?,?,?,?,?,?,?)
                            """, (t_id, datetime.now(), False,
                                  *(tr_clean.loc[ind, DATA_SCHEMA_CLEAN].values.tolist()))
                        ).fetchall()
                    c += 1
                    self.connection.commit()
        logger.info("Done {} transactions from MONOBANK. All transaction num = {}.".format(
            c, tr.index.shape[0]
        ))

    def _post_privatbank(self, tr):
        tr = tr[DATA_SCHEMA].reset_index(drop=True)
        tr_clean = get_clean_pb_data(tr)
        tr["@pb_id"] = tr.apply(
            lambda r: (r.loc["@card"][-4:] + "|" +
                       r.loc["@rest"] + "|" +
                       r.loc["@trandate"]),
            axis=1)
        c = 0
        for ind in tr.index.tolist():
            with self.connection:
                t_id = self.get_t_id("TransactionsRaw")

                if not self.existing_transaction(tr.loc[ind, "@pb_id"]):
                    self.cursor.execute(
                        """
                        INSERT INTO TransactionsRaw VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """, (t_id, *(tr.loc[ind, ['@pb_id'] + DATA_SCHEMA].values.tolist()))
                    ).fetchall()
                    if ind in tr_clean.index.tolist():
                        self.cursor.execute(
                            """
                            INSERT INTO Transactions VALUES (?,?,?,?,?,?,?,?,?,?,?)
                            """, (t_id, datetime.now(), False,
                                  *(tr_clean.loc[ind, DATA_SCHEMA_CLEAN].values.tolist()))
                        ).fetchall()
                    self.connection.commit()
        logger.info("Done {} transactions from PRIVATBANK. All transaction num = {}.".format(
            c, tr.index.shape[0]
        ))

    def get_trans_on_dates(self, start_date, end_date=None, data_type="clean"):

        table_name = "Transactions"
        if data_type == "raw":
            table_name += "Raw"

        if end_date:
            with self.connection:
                return self.cursor.execute(
                    """
                    SELECT * FROM {} WHERE trandate < ? AND trandate >= ? """.format(table_name),
                    (end_date, start_date)
                ).fetchall()
        else:
            with self.connection:
                return self.cursor.execute(
                    """
                    SELECT * FROM {} WHERE trandate = ? """.format(table_name),
                    (start_date, )
                ).fetchall()
