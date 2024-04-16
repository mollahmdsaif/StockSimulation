import heapq
import os
import time

from Stock import *


class StockCollection:
    STOCKCOLLECTION_CACHE_FILE = 'cache/StockCollectionCache.json'

    def __init__(self, cached=False, counter=False):
        # {date_i: heapq(
        #                  (initial_i_(max_mul), high_i(max_mul)low_i-(max_mul)1, volume_i(max_mul)),
        #                  (initial_i_(2nd_max_mul), high_i(2nd_max_mul)low_i-(2nd_max_mul)1, volume_i(2nd_max_mul)),
        #              ),
        # }
        self.data_dict = {}
        self.cached = cached
        self.counter = counter
        self.stock_volume_dict = {}
        self.retrieval_failed_lst = []

        if cached:
            self.retrieval()
        else:
            self.upload()

    def upload(self):
        self.get_stock_initial_volume()
        self.parse_stock_data()
        with open(StockCollection.STOCKCOLLECTION_CACHE_FILE, 'w') as f:
            f.write(json.dumps(self.data_dict, indent=4))

        print('Retrieval Failed List:')
        print('\n'.join(self.retrieval_failed_lst))

    def retrieval(self):
        if not os.path.exists(StockCollection.STOCKCOLLECTION_CACHE_FILE):
            self.upload()
        else:
            with open(StockCollection.STOCKCOLLECTION_CACHE_FILE, 'r') as f:
                self.data_dict = json.loads(f.read())

    def get_stock_initial_volume(self):
        with open('resources/stock_lst.txt', 'r') as f:
            for initial_volume in f.read().strip().split('\n'):
                initial, volume = initial_volume.split('\t')
                self.stock_volume_dict[initial] = volume

    def parse_stock_data(self):
        left, done, s_time, e_time, avg_time = len(self.stock_volume_dict), 0, 0, 0, 0
        for initial in self.stock_volume_dict:
            s_time = time.time_ns()
            volume = float(self.stock_volume_dict[initial])
            try:
                stock_i = Stock(initial,
                                os.path.exists(f'cache/{initial}.json'),
                                volume)
                for date, multiple_mar_cap in stock_i.data_dict.items():
                    if multiple_mar_cap is None:
                        continue
                    else:
                        multiple, mar_cap = multiple_mar_cap
                    self.data_dict[date] = self.data_dict.get(date, [])
                    if multiple is not None:
                        heapq.heappush(self.data_dict[date], (-multiple, initial, mar_cap))
                e_time = time.time_ns()
            except Exception as e:
                print(e)
                e_time = 0
                self.retrieval_failed_lst.append(initial)

            if self.counter:
                if not e_time == 0:
                    if avg_time == 0:
                        avg_time = (e_time - s_time) / 2
                    else:
                        avg_time = (avg_time + e_time - s_time) / 2
                    done += 1
                    left -= 1
                print(f'Done: {done} Left: {left} Time Remaining: {(avg_time * left) / (10 ** 9)}')

    def calculate_profit(self, start_date, end_date, net_initial, min_profit, max_profit, part_of_market_cap):
        net_worth = net_initial
        net_multiple = 1
        transaction_cnt = 0

        print(f'Initial: {net_initial}')
        print('Transactions:')
        for date in self.data_dict:
            for multiple, initial, mar_cap in self.data_dict[date]:
                multiple = -multiple
                temp_net = net_worth * multiple
                if temp_net * part_of_market_cap < mar_cap and start_date < date < end_date and min_profit < multiple < max_profit:
                    net_worth = temp_net
                    net_multiple *= multiple
                    transaction_cnt += 1
                    if net_worth >= 1000000:
                        net = f'{(net_worth / 1000000): >6.2f}M'
                    elif net_worth >= 1000:
                        net = f'{(net_worth / 1000): >6.2f}K'
                    else:
                        net = f'{net_worth : >6.2f}'
                    stock_initial = initial.center(10, ' ')
                    print(date, f'{stock_initial}\t{multiple : >6.2f}', net, sep='\t')
                    break

        print(f'Total Transactions: {transaction_cnt}')
        print(f'Total Multiple: {net_multiple}')

        while input('To Continue Enter \'c\' : \n') == 'c':
            self.calculate_profit(input('start_date: '),
                                  input('end_date: '),
                                  float(input('net_initial: ')),
                                  float(input('min_profit: ')),
                                  float(input('max_profit: ')),
                                  float(input('part_of_market_cap: ')))
