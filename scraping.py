from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "https://myanimelist.net/topmanga.php?type=bypopularity"

response = urlopen(url)
html = response.read()

soup = BeautifulSoup(html, "html.parser")
popularMangas = list(map(lambda a: a.text, soup.select('a.fs14')))
print(popularMangas)