from datetime import datetime as dt, timezone
import json
from pandas import read_csv as read_csv


class Stock:
    START_DATE_UTC = '2017-01-01'
    END_DATE_UTC = '2021-06-01'
    STOCK_VOLUMES = None

    def __init__(self, initial, cached=False, volume=None):
        self.initial = initial
        self.data_dict = None  # {date_i: high_i/low_i-1, }
        self.cached = cached
        self.volume = volume
        self.cache_file_name = f'cache/{initial}.json'

        if cached:
            self.retrieve(self.cache_file_name)
        else:
            self.upload(self.cache_file_name)

    def upload(self, cache_file_name):
        url_link = Stock.get_link(self.initial)
        # __0_______1_______2_______3______4________5____________6
        # ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        data = read_csv(url_link, header=None).values.tolist()[1::]
        self.data_dict = Stock.get_all_dates(dict)
        for i, (date, opening, high, low, closing, adj_closing, vol) in enumerate(data):
            mul = 1
            mar_cap = 1
            if i != 0:
                mar_cap = float(opening) * float(self.volume)
                mul = float(high) / float(data[i - 1][3])
            self.data_dict[date] = (mul, mar_cap)
        with open(cache_file_name, 'w') as f:
            f.write(json.dumps(self.data_dict, indent=4))

    def retrieve(self, cache_file_name):
        try:
            with open(cache_file_name, 'r') as f:
                self.data_dict = json.loads(f.read())
        except Exception as e:
            print(e, cache_file_name, 'not found')

    @classmethod
    def get_link(cls, initial):
        start = Stock.create_utc_stamp(Stock.START_DATE_UTC)
        end = Stock.create_utc_stamp(Stock.END_DATE_UTC)
        url = ['https://query1.finance.yahoo.com/v7/finance/download/',
               '?period1=',
               '&period2=',
               '&interval=',
               '&events=history&includeAdjustedClose=true']
        return f'{url[0]}{initial}{url[1]}{start}{url[2]}{end}{url[3]}1d{url[4]}'

    @classmethod
    def create_utc_stamp(cls, date):
        return int(dt.strptime(date, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())

    @classmethod
    def get_all_dates(cls, dates_type=dict):
        dates = None
        with open('resources/dates.txt', 'r') as f:
            if dates_type == dict:
                dates = dict.fromkeys(f.read().strip().split('\n'), None)
            else:
                dates = f.read().strip().split('\n')
        return dates
