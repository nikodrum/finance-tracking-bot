import sqlite3
from datetime import datetime


def database_init(database_path):
    connection = sqlite3.connect(database_path, check_same_thread=False)
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
                pb_id str,
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