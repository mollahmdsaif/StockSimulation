from StockCollection import *


def main():
    s = StockCollection(True, False)
    # (start_date, end_date, net_initial, min_profit, max_profit, part_of_market_cap)
    s.calculate_profit('2017-08-01', '2020-03-01', 200, 1.4, 5, 400)


if __name__ == '__main__':
    main()
