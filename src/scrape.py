import requests
from bs4 import BeautifulSoup
from vars.website1 import *

URL = f"https://{DOMAIN}"

response = requests.get(URL)

soup = BeautifulSoup(response.content, "html.parser")

title = soup.title

print("Page Title:", title.text)
