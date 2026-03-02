#!/usr/bin/env python3
import sys
import time
import httpx
from bs4 import BeautifulSoup

def get_financial_data(ticker, field):
    """Fetch and parse financial data from Yahoo Finance using httpx."""
    
    url = f"https://finance.yahoo.com/quote/{ticker}/financials/?p={ticker.lower()}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # Use httpx with HTTP/2 support for better performance
        with httpx.Client(http2=True, timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', string=field)
            if div:
                parent_row = div.find_parent('div', class_='row')
                if parent_row:
                    result = []
                    for i in parent_row.children:
                        if i.text.strip() != "":
                            result.append(i.text.strip())
        
                    if len(result) > 1:
                        return tuple(result)
            
            return (f"Field '{field}' not found for {ticker}",)
        
    except httpx.RequestError as e:
        # Handles network errors, timeouts, etc.
        return (f"Error fetching data: {e}",)
    except httpx.HTTPStatusError as e:
        # Handles HTTP 4xx/5xx errors
        return (f"HTTP error {e.response.status_code}: {e}",)
    except Exception as e:
        return (f"Error parsing data: {e}",)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./financial_enhanced.py <ticker> <field>")
        print("Example: ./financial_enhanced.py MSFT 'Total Revenue'")
        sys.exit(1)
    
    result = get_financial_data(sys.argv[1], sys.argv[2])
    print(result)

if __name__ == "__main__":
    main()