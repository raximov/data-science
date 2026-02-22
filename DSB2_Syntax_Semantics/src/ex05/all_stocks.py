import sys


def all_stocks():
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

    arg = sys.argv[1]
    parts = arg.split(',')

    for part in parts:
        stripped = part.strip()
        if stripped == '':
            return

    companies_lower = {k.lower(): k for k in COMPANIES}
    stocks_upper = {k.upper(): k for k in STOCKS}

    for part in parts:
        expression = part.strip()
        expression_lower = expression.lower()
        expression_upper = expression.upper()

        if expression_lower in companies_lower:
            original_name = companies_lower[expression_lower]
            ticker = COMPANIES[original_name]
            print(f"{original_name} stock price is {STOCKS[ticker]}")
        elif expression_upper in stocks_upper:
            original_ticker = stocks_upper[expression_upper]
            ticker_to_company = {v: k for k, v in COMPANIES.items()}
            company = ticker_to_company[original_ticker]
            print(f"{original_ticker} is a ticker symbol for {company}")
        else:
            print(f"{expression} is an unknown company or an unknown ticker symbol")


if __name__ == '__main__':
    all_stocks()
