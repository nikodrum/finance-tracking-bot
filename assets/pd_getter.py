from datetime import datetime, timedelta
from requests import post
from hashlib import sha1, md5
from assets.config import DATA_SCHEMA, PRIVAT_API
import xmltodict
import pandas as pd


class PrivatBankAPIWrapper:

    def __init__(self, configs):
        self.configs = configs

    @staticmethod
    def parse_response(response):
        data_list = [tr for tr in response["response"]["data"]["info"]["statements"]["statement"]]
        response = pd.DataFrame.from_dict(data_list).drop_duplicates()
        if 0 not in response.columns:
            return response

    @staticmethod
    def format_date(date_str):
        return datetime.strftime(date_str, "%d.%m.%Y")

    @staticmethod
    def get_operations(config, start_date, end_date):
        data_string = str(
            """<oper>cmt</oper><wait>0</wait><test>0</test><payment id=""><prop name="sd" value="{}" /><prop name="ed" value="{}" /><prop name="cardnum" value="{}" /></payment>""".format(
                start_date,
                end_date,
                config["card_number"]
            ))

        m = md5((data_string + config["merch_pass"]).encode("utf-8")).hexdigest()
        s = sha1(m.encode("utf-8")).hexdigest()

        r_xml = """<?xml version="1.0" encoding="UTF-8"?><request version="1.0"><merchant><id>{}</id><signature>{}</signature></merchant><data><oper>cmt</oper><wait>0</wait><test>0</test><payment id=""><prop name="sd" value="{}" /><prop name="ed" value="{}" /><prop name="cardnum" value="{}" /></payment></data></request>""".format(
            config["merch_id"],
            s,
            start_date,
            end_date,
            config["card_number"]
        )

        res = post(PRIVAT_API, data=r_xml, headers={'Content-Type': 'application/xml; charset=UTF-8'})
        dict_response = xmltodict.parse(res.content.decode())
        return dict_response

    def get_today(self):
        response = pd.DataFrame(columns=DATA_SCHEMA)
        start_date = datetime.now().date()
        end_date = (datetime.now() + timedelta(days=1)).date()

        for config in self.configs:

            raw_data = self.get_operations(
                config=config,
                start_date=self.format_date(start_date),
                end_date=self.format_date(end_date)
            )
            try:
                data = self.parse_response(raw_data)
                data = data[data['@trandate'] == str(datetime.now().date())]
            except KeyError:
                data = pd.DataFrame(columns=DATA_SCHEMA)

            response = response.append(data)
        return response

    def get_yesterday(self):
        response = pd.DataFrame(columns=DATA_SCHEMA)
        start_date = (datetime.now() - timedelta(days=1)).date()
        end_date = datetime.now().date()

        for config in self.configs:

            raw_data = self.get_operations(
                config=config,
                start_date=self.format_date(start_date),
                end_date=self.format_date(end_date)
            )
            try:
                data = self.parse_response(raw_data)
                data = data[data['@trandate'] == str(start_date)]
            except KeyError:
                data = pd.DataFrame(columns=DATA_SCHEMA)

            response = response.append(data)
        return response

    def get_dates(self, start_date, end_date=None):
        response = pd.DataFrame(columns=DATA_SCHEMA)
        start_date = datetime.strptime(str(start_date)[:10], "%Y-%m-%d").date()

        if end_date:
            end_date = datetime.strptime(str(end_date)[:10], "%Y-%m-%d")
        else:
            end_date = (start_date + timedelta(days=1))

        for config in self.configs:

            raw_data = self.get_operations(
                config=config,
                start_date=self.format_date(start_date),
                end_date=self.format_date(end_date)
            )
            try:
                data = self.parse_response(raw_data)
                data = data[(data['@trandate'] >= str(start_date)) &
                            (data['@trandate'] < str(end_date))]
            except KeyError:
                data = pd.DataFrame(columns=DATA_SCHEMA)

            response = response.append(data)
        return response
