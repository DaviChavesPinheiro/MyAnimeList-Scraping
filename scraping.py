from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import json
import re

def openMyAnimeListMangasPage(url, startPage, pagesAmount):
    myAnimeListMangasPage = []
    for pageIndex in range(startPage, startPage + pagesAmount):
            req = Request(url + str(pageIndex * 50), headers=headers)
            response = urlopen(req)
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")

            for mangaTile in soup.select(".ranking-list"):
                title = mangaTile.select_one('.hoverinfo_trigger.fs14.fw-b').text
                detailPage = mangaTile.select_one(".hoverinfo_trigger.fs14.fw-b")['href']
                myAnimeListMangasPage.append({'title': title, 'detailPage': detailPage})
    return myAnimeListMangasPage
            
def openDetailPageManga(manga):
    req = Request(manga['detailPage'], headers=headers)
    response = urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")

    column = soup.select_one('td div')

    img = soup.find("img", {"itemprop": "image"}).get('data-src') or soup.find("img", {"itemprop": "image"}).get('src')
    # img = soup2.select("img[]")[2].get('data-src') or soup2.select("img")[2].get('src')
    # print(soup2.select("img")[2])
    information = column.getText()
    information = re.split(
        'Volumes:|Chapters:|Status:|Published:|Genres:|Authors:|StatisticsScore:|Members:|Serialization:|scored|Favorites:', " ".join(information.split()))

    genres = information[5].strip().replace(" ", "").split(",")
    for index, genre in enumerate(genres):
        genres[index] = genre[:int(len(genre) / 2)]
    genres = ", ".join(genres)
    
    return {'title': manga['title'].strip(), "thumbnail": img, "description": "Description", "chapters": [], "volumes": information[1].strip(), "chaptersAmount": information[2].strip(), "status": information[3].strip(), "published": information[4].strip(),
                            "genres": genres, "authors": information[6].strip(), "score": information[8].replace("(", "").strip(), "members": information[10].strip()}
    
def openGoogleSearchPage(manga):
    manga['unionMangasSite'] = ""
    req = Request("https://www.google.com/search?q=union+mangas+" + str(manga['title']).lower().replace(" ", "+"), headers=headers)
    response = urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    results = soup.select_one("#search")
    for result in results:
        if ("unionmangas.top/perfil-manga/" in str(result.select_one("a").get("href"))):
            manga['unionMangasSite'] = result.select_one("a").get("href")
    return manga

def openUnionMangaDetails(manga):
    if(manga['unionMangasSite'] != ''):
        req = Request(manga['unionMangasSite'], headers=headers)
        response = urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        
        chaptersElements = soup.select(".row.lancamento-linha")
        chaptersElements.reverse()
        
        manga['description'] = soup.select_one(".panel-body").getText().strip()
        chapters = []
        for release in chaptersElements:
            chapters.append({'title': release.a.getText().strip(), 'pagesLink': release.a.get('href')})
        manga['chapters'] = chapters
        
    del manga['unionMangasSite']
    return manga

def openMangaPagesLink(manga, index):
    chapter = manga['chapters'][index]
    
    if(len(manga['chapters']) == 0):
        print("MANGA NAO POSSUI CAPITULOS")
        return manga
    pages = []
    req = Request(manga['chapters'][index]['pagesLink'], headers=headers)
    response = urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    for page in soup.select("img"):
        pages.append(page.get('src'))
    
    chapter['pages'] = pages
    del chapter['pagesLink']
    return chapter


mangas = []
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
if __name__ == '__main__':
    startPage = int(input("Enter the Start Page: "))
    pagesAmount = int(input("Enter the number of pages that you want to Scrap: "))

    url = "https://myanimelist.net/topmanga.php?type=bypopularity&limit="
    
    # myAnimeListMangasPage = []
    try:
        mangas = openMyAnimeListMangasPage(url, startPage, pagesAmount)
        # {title, detailPageURL}
        # mangas = mangas[:2]
        print(mangas)
    except HTTPError as e:
        print(e.status, e.reason)
        print("openMyAnimeListMangasPage error...")
    except URLError as e:
        print(e.reason)
        print("openMyAnimeListMangasPage error...")
    
    for index, manga in enumerate(mangas):
        try:
            mangaWithDetail = openDetailPageManga(manga)
            mangas[index] = mangaWithDetail
            # {title, Volumes, Chapters, Status, Published, Genres, Authors, StatisticsScore, Members, Serialization, scored, Favorites}
            with open('data.json', 'w') as outfile:
                json.dump(mangas, outfile)
            print(mangas[index])
        except HTTPError as e:
            print(e.status, e.reason)
            print("openDetailPageManga error...")
        except URLError as e:
            print(e.reason)
            print("openDetailPageManga error...")
    
    for index, manga in enumerate(mangas):
        try:
            mangaWithChaptersPageLink = openGoogleSearchPage(manga)
            mangas[index] = mangaWithChaptersPageLink
            # {unionMangasSite, title, Volumes, Chapters, Status, Published, Genres, Authors, StatisticsScore, Members, Serialization, scored, Favorites}
            with open('data.json', 'w') as outfile:
                json.dump(mangas, outfile)
            print(mangas[index])
        except HTTPError as e:
            print(e.status, e.reason)
            print("openGoogleSearchPage error...")
        except URLError as e:
            print(e.reason)
            print("openGoogleSearchPage error...")
    
    for index, manga in enumerate(mangas):
        try:
            mangaWithChaptersPageLink = openUnionMangaDetails(manga)
            mangas[index] = mangaWithChaptersPageLink
            # {title, Volumes, Chapters, Status, Published, Genres, Authors, StatisticsScore, Members, Serialization, scored, Favorites}
            with open('data.json', 'w') as outfile:
                json.dump(mangas, outfile)
            print(mangas[index])
        except HTTPError as e:
            print(e.status, e.reason)
            print("openUnionMangaDetails error...")
        except URLError as e:
            print(e.reason)
            print("openUnionMangaDetails error...")
            
    for index, manga in enumerate(mangas):
        for chapterIndex, chapter in enumerate(manga['chapters']):
            try:
                chapterWithPages = openMangaPagesLink(manga, chapterIndex)
                # del mangas[index]['chapters'][chapterIndex]['pagesLink']
                mangas[index]['chapters'][chapterIndex] = chapterWithPages
                # {title, Volumes, Chapters, Status, Published, Genres, Authors, StatisticsScore, Members, Serialization, scored, Favorites}
                
                print("Manga " + manga['title'] + ". Chapter " + str(chapterIndex) + " getted.")
            except HTTPError as e:
                print(e.status, e.reason)
                print("openMangaPagesLink error...")
            except URLError as e:
                print(e.reason)
                print("openMangaPagesLink error...")
                
        print()
        print(manga['title'])
        print(manga['chapters'])
        with open('data.json', 'w') as outfile:
                json.dump(mangas, outfile)
    print("FINISH")
    # try:
    #     for pageIndex in range(startPage, startPage + pagesAmount):
    #         req = Request(url + str(pageIndex * 50), headers=headers)
    #         response = urlopen(req)
    #         html = response.read()
    #         soup = BeautifulSoup(html, "html.parser")

    #         for mangaTile in soup.select(".ranking-list"):
    #             title = mangaTile.select_one('.hoverinfo_trigger.fs14.fw-b').text
    #             print(title)
    #             detailPage = mangaTile.select_one(
    #                 ".hoverinfo_trigger.fs14.fw-b")['href']

    #             req2 = Request(detailPage, headers=headers)
    #             response2 = urlopen(req2)
    #             html2 = response2.read()
    #             soup2 = BeautifulSoup(html2, "html.parser")

    #             column = soup2.select_one('td div')

    #             img = soup2.find("img", {"itemprop": "image"}).get('data-src') or soup2.find("img", {"itemprop": "image"}).get('src')
    #             # img = soup2.select("img[]")[2].get('data-src') or soup2.select("img")[2].get('src')
    #             # print(soup2.select("img")[2])
    #             information = column.getText()
    #             information = re.split(
    #                 'Volumes:|Chapters:|Status:|Published:|Genres:|Authors:|StatisticsScore:|Members:|Serialization:|scored|Favorites:', " ".join(information.split()))

    #             genres = information[5].strip().replace(" ", "").split(",")
    #             for index, genre in enumerate(genres):
    #                 genres[index] = genre[:int(len(genre) / 2)]
    #             genres = ", ".join(genres)
                
    #             #Google search by Union Mangas $title
    #             description = "Descrição"
    #             chapters = []
    #             req3 = Request("https://www.google.com/search?q=union+mangas+" + str(title).lower().replace(" ", "+"), headers=headers)
    #             response3 = urlopen(req3)
    #             html3 = response3.read()
    #             soup3 = BeautifulSoup(html3, "html.parser")
    #             results = soup3.select_one("#search")
    #             for result in results:
    #                 # print(result)
    #                 if ("unionmangas.top/perfil-manga/" in str(result.select_one("a").get("href"))):
    #                     unionMangasPage = result.select_one("a").get("href")
    #                     req4 = Request(unionMangasPage, headers=headers)
    #                     response4 = urlopen(req4)
    #                     html4 = response4.read()
    #                     soup4 = BeautifulSoup(html4, "html.parser")
    #                     description = soup4.select_one(".panel-body").getText().strip()
    #                     chaptersElements = soup4.select(".row.lancamento-linha")
    #                     chaptersElements.reverse()
    #                     for release in chaptersElements:
    #                         pages = []
    #                         # Get All Pages Links
    #                         req5 = Request(release.a.get('href'), headers=headers)
    #                         response5 = urlopen(req5)
    #                         html5 = response5.read()
    #                         soup5 = BeautifulSoup(html5, "html.parser")
    #                         for page in soup5.select("img"):
    #                             pages.append(page.get('src'))
    #                         print("Chapter " + release.a.getText().strip() + " Getted")
    #                         chapters.append({'title': release.a.getText().strip(), 'pages': pages})
    #                         if(len(chapters) >= 7): 
    #                             break
    #                     # chapters.reverse()
    #                     break
                
    #             mangas.append({'title': title.strip(), "thumbnail": img, "description": description, "chapters": chapters, "volumes": information[1].strip(), "chaptersAmount": information[2].strip(), "status": information[3].strip(), "published": information[4].strip(),
    #                         "genres": genres, "authors": information[6].strip(), "score": information[8].replace("(", "").strip(), "members": information[10].strip()})
    #             with open('data.json', 'w') as outfile:
    #                 json.dump(mangas, outfile)
    #             print(mangas[len(mangas) - 1])
    #     print(mangas)
    #     print(len(mangas))
    #     with open('data.json', 'w') as outfile:
    #         json.dump(mangas, outfile)


    # except HTTPError as e:
    #     print(e.status, e.reason)
    # except URLError as e:
    #     print(e.reason)



