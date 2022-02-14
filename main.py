import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
import itertools
import time

def getServerUrl(server):
    url = "https://dostats.info/HallOfFame?Server="+server
    return url

def getStats(soup):
    info = []
    values = []
    names = []

    for div in soup.find_all('div',attrs={'class':'col'}, limit = 20):
        if len(div['class']) == 1:
            div_text = div.get_text(strip=True)
            info.append(div_text)


    for table in soup.find_all("table", limit = 4):
        rows = []
        for tr in table.find_all("tr"):
            row = []
            for td in tr.find_all("td", attrs= {'class' : 'td-right'}):
                td_values = td.get_text(strip=True)
                row.append(td_values)
            rows.append(row)
        values.extend(list(zip(*[x for x in rows if x != []])))
    values = list(itertools.chain.from_iterable(values))

    table = soup.find("table", attrs={'id': 'Pagination'})
    body = table.find("tbody")
    for td in body.find_all("td"):
        td_names = td.get_text(strip=True)
        names.append(td_names)

    return info+values+names

#### Main


def main():

    # servers = ["de2", "de4","es1","fr1","int2","int6","gbl1","int1","int5","int7","int11","int14","mx1","pl3","ru1","ru5","tr3","tr4","tr5","us2"]
    servers = ["es1", "int1", "gbl1"]
    counter = 1

    # Setting up the headers for the csv file

    headers1 = ["Name", "Server", "Company", "Rank", "Level", "Reg", "Hours", "Achievements", "Position In Rank", "Estimated RP"]
    headers2 = ["Topuser","Experience","Honor","NPCs","Kills","Alpha","Beta","Gamma","Delta","Epsilon","Zeta","Kappa","Lambda","Kronos","Hades","Kuiper","Hours"]
    timeHeaders = ["Current", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 100 Days", "Last Year"]
    for i  in range (len(headers2)):
        for time in timeHeaders:
            headers1.append(headers2[i]+" "+time)

    # Find every server page

    for i in range (len(servers)):
        page = BeautifulSoup(urlopen(Request(getServerUrl(servers[i]), headers = {'User-Agent': 'Mozilla/5.0'})).read(), "html.parser")
        links = []
        playerstats = []

        # Find every player url in each server page

        for j in page.find_all("a", href = re.compile("Profile")):
            player = "https://dostats.info"+j["href"], j.get_text(strip=True)
            links.append(player)

            # Open and process every player page

            playerpage = BeautifulSoup(urlopen(Request(player[0],headers= {'User-Agent': 'Mozilla/5.0'})).read(),"html.parser")
            playerstats.append(getStats(playerpage))
            print("Player " + str(counter) + " " + servers[i] + " stats done")
            counter += 1

        # We save top 100 player links in a csv file for this server

        with open("links/"+servers[i]+"top100userlinks.csv", "w", encoding="utf-8", newline='') as file:
            write = csv.writer(file)
            write.writerow(["Link","Player Name"])
            write.writerows(links)

        # We save in a big csv table every player stat for this server

        with open("stats/"+servers[i]+"top100playerstats.csv", "w", encoding = "utf-8", newline='') as file:
            write = csv.writer(file)
            write.writerow(headers1)
            write.writerows(playerstats)

        print("\n --- SERVER " + servers[i] + " STATS DONE ---\n")
        counter = 1


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
