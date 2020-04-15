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

            img = soup2.find("img", {"itemprop": "image"}).get('data-src') or soup2.find("img", {"itemprop": "image"}).get('src')
            # img = soup2.select("img[]")[2].get('data-src') or soup2.select("img")[2].get('src')
            # print(soup2.select("img")[2])
            information = column.getText()
            information = re.split(
                'Volumes:|Chapters:|Status:|Published:|Genres:|Authors:|StatisticsScore:|Members:|Serialization:|scored|Favorites:', " ".join(information.split()))

            genres = information[5].strip().replace(" ", "").split(",")
            for index, genre in enumerate(genres):
                genres[index] = genre[:int(len(genre) / 2)]
            genres = ", ".join(genres)
            
            #Google search by Union Mangas $title
            description = "Descrição"
            chapters = []
            req3 = Request("https://www.google.com/search?q=union+mangas+" + str(title).lower().replace(" ", "+"), headers=headers)
            response3 = urlopen(req3)
            html3 = response3.read()
            soup3 = BeautifulSoup(html3, "html.parser")
            results = soup3.select_one("#search")
            for result in results:
                # print(result)
                if ("unionmangas.top/perfil-manga/" in str(result.select_one("a").get("href"))):
                    unionMangasPage = result.select_one("a").get("href")
                    req4 = Request(unionMangasPage, headers=headers)
                    response4 = urlopen(req4)
                    html4 = response4.read()
                    soup4 = BeautifulSoup(html4, "html.parser")
                    description = soup4.select_one(".panel-body").getText().strip()
                    for release in soup4.select(".row.lancamento-linha"):
                        pages = []
                        # Get All Pages Links
                        req5 = Request(release.a.get('href'), headers=headers)
                        response5 = urlopen(req5)
                        html5 = response5.read()
                        soup5 = BeautifulSoup(html5, "html.parser")
                        for page in soup5.select("img"):
                            pages.append(page.get('src'))
                        print("Chapter" + release.a.getText().strip() + "Getted")
                        chapters.append({'title': release.a.getText().strip(), 'pages': pages})
                    chapters.reverse()
                    break
            
            mangas.append({'title': title.strip(), "thumbnail": img, "description": description, "chapters": chapters, "volumes": information[1].strip(), "chaptersAmount": information[2].strip(), "status": information[3].strip(), "published": information[4].strip(),
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
