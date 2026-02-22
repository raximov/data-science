import sys


def stock_prices():
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

    company_input = sys.argv[1]
    companies_lower = {k.lower(): v for k, v in COMPANIES.items()}
    ticker = companies_lower.get(company_input.lower())

    if ticker is None:
        print("Unknown company")
    else:
        print(STOCKS[ticker])


if __name__ == '__main__':
    stock_prices()
