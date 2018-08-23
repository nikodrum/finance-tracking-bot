import pandas as pd
from datetime import datetime as dt
from assets.config import DATA_SCHEMA, DATA_SCHEMA_CLEAN
import csv


def get_clean_pb_data(data):
    data = data[DATA_SCHEMA].dropna(axis=0)

    expense = data[data["@cardamount"].map(lambda row: float(row.split(" ")[0])) < 0]

    clean_data = pd.DataFrame()
    clean_data["category"] = expense["@description"].map(lambda row: row.split(":")[0])
    clean_data["subcategory"] = expense["@description"].map(lambda row: row.split(":")[0])
    clean_data["trandate"] = expense["@trandate"]
    clean_data["trantime"] = expense["@trantime"]
    clean_data["amount"] = expense["@amount"].map(lambda row: abs(float(row.split(" ")[0])))
    clean_data["amount_currency"] = expense["@amount"].map(lambda row: row.split(" ")[-1])
    clean_data["cardamount"] = expense["@cardamount"].map(lambda row: abs(float(row.split(" ")[0])))
    clean_data["store"] = expense["@terminal"]

    return clean_data[DATA_SCHEMA_CLEAN]


def get_clean_mono_data(data):

    data['@amount'] = data["@amount"].map(lambda r: r.split(" ")[0]).astype(float)

    data = data[data["@amount"] < 0]
    clean_data = pd.DataFrame()

    clean_data["trandate"] = data['@trandate'].map(lambda r: str(dt.strptime(r, "%d.%m.%Y").date()))
    clean_data["category"] = None
    clean_data["subcategory"] = None
    clean_data["trantime"] = None
    clean_data["amount"] = data["@amount"].map(abs)
    clean_data["amount_currency"] = "UAH"
    clean_data["cardamount"] = data["@amount"].map(abs)
    clean_data["store"] = data["@description"]

    return clean_data[DATA_SCHEMA_CLEAN]


def get_raw_mono_data(data):

    data = data.replace("\n+", " +")
    data = list(csv.reader(data.split("\n")))[:-1]

    data = pd.DataFrame(
        data, columns=['date', 'details', 'amount', 'commission_amount', 'cashback', 'rest']
    )

    response_df = pd.DataFrame()
    response_df['@trandate'] = data['date']
    response_df['@card'] = 5375414100218154
    response_df['@appcode'] = None
    response_df['@trantime'] = None
    response_df['@amount'] = data['amount'].astype(str) + " UAH"
    response_df['@cardamount'] = data['amount'].astype(str) + " UAH"
    response_df['@rest'] = data['rest'].astype(str) + " UAH"
    response_df['@terminal'] = None
    response_df['@description'] = data['details']

    return response_df[DATA_SCHEMA]
