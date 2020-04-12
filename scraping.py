from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

url = "https://unionleitor.top/perfil-manga/shingeki-no-kyojin"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

def process_html(input):
    return " ".join(input.split()).replace("> <", "><")

try:
    req = Request(url, headers = headers)
    response = urlopen(req)
    html = response.read()
    html = html.decode('utf-8') # Decode Bytes to String in utf-8 encoding
    html = process_html(html)
    soup = BeautifulSoup(html, "html.parser")
    print(soup.html.head.title) #Browse through tags
    print(soup.html.head.title.getText())#Get text from tag
    print(soup.img.attrs)#Get attributes of the first image found
    print(soup.img.attrs.keys())
    print(soup.img.attrs.values())
    print(soup.img['src'])
    print(soup.img.get('src'))
except HTTPError as e:
    print(e.status, e.reason)
except URLError as e:
    print(e.reason)
# popularMangas = list(map(lambda a: a.text, soup.select('a.fs14')))
