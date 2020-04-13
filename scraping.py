from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import json
import re

url = "https://myanimelist.net/topmanga.php?type=bypopularity&limit="
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
page = 0
try:
    mangas = []
    for i in range(2):
        req = Request(url + str(i * 50), headers=headers)
        response = urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")

        for mangaTile in soup.select(".ranking-list"):
            title = mangaTile.select_one('.hoverinfo_trigger.fs14.fw-b').text
            print(title)
            detailPage = mangaTile.select_one(
                ".hoverinfo_trigger.fs14.fw-b")['href']

            req2 = Request(detailPage, headers=headers)
            response2 = urlopen(req2)
            html2 = response2.read()
            soup2 = BeautifulSoup(html2, "html.parser")

            column = soup2.select_one('td div')
        
            img = soup2.select("img")[2].get('data-src')
            # print(soup2.select("img")[2])
            information = column.getText()
            information = re.split(
                'Volumes:|Chapters:|Status:|Published:|Genres:|Authors:|StatisticsScore:|Members:|Serialization:|scored|Favorites:', " ".join(information.split()))

            genres = information[5].strip().replace(" ", "").split(",")
            for index, genre in enumerate(genres):
                genres[index] = genre[:int(len(genre) / 2)]
            genres = ", ".join(genres)
            
            mangas.append({'title': title.strip(), "image": img, "volumes": information[1].strip(), "chapters": information[2].strip(), "status": information[3].strip(), "published": information[4].strip(),
                        "genres": genres, "authors": information[6].strip(), "score": information[8].replace("(", "").strip(), "members": information[10].strip()})
            print(mangas[len(mangas) - 1])
    print(mangas)
    print(len(mangas))
    with open('data.json', 'w') as outfile:
        json.dump(mangas, outfile)


except HTTPError as e:
    print(e.status, e.reason)
except URLError as e:
    print(e.reason)
# popularMangas = list(map(lambda a: a.text, soup.select('a.fs14')))
