import pandas as pd
from assets.config import DATA_SCHEMA, DATA_SCHEMA_CLEAN


def get_clean_data(data):

    data = data[DATA_SCHEMA].dropna(axis=0).reset_index(drop=True)

    expense = data[data["@amount"].map(lambda row: float(row.split(" ")[0])) < 0]

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
