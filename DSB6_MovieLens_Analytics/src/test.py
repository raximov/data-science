import urllib.request
from bs4 import BeautifulSoup

url = "https://www.imdb.com/title/tt0114709/"

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
)

response = urllib.request.urlopen(req)

html = response.read()

soup = BeautifulSoup(html, "html.parser")

print(response.status)
print(soup.title)
print(html[:500])