import requests
from bs4 import BeautifulSoup

DOMAIN = "DOMAIN"

URL = f"https://{DOMAIN}"

response = requests.get(URL)

soup = BeautifulSoup(response.content, "html.parser")

title = soup.title

print("Page Title:", title.text)
