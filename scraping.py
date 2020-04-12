from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

# url = "https://myanimelist.net/manga/11/Naruto"
# headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}


urlretrieve("https://cdn.myanimelist.net/images/manga/3/117681.jpg", "./teste.jpg")
    
    
