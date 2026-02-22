import sys


def ticker_symbols():
    COMPANIES = {
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Netflix': 'NFLX',
        'Tesla': 'TSLA',
        'Nokia': 'NOK'
    }

    STOCKS = {
        'AAPL': 287.73,
        'MSFT': 173.79,
        'NFLX': 416.90,
        'TSLA': 724.88,
        'NOK': 3.37
    }

    if len(sys.argv) != 2:
        return

    ticker_input = sys.argv[1].upper()
    ticker_to_company = {v: k for k, v in COMPANIES.items()}

    if ticker_input not in STOCKS:
        print("Unknown ticker")
    else:
        company = ticker_to_company[ticker_input]
        print(f"{company} {STOCKS[ticker_input]}")


if __name__ == '__main__':
    ticker_symbols()
