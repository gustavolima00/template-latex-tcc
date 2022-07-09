import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup
import threading

sem = threading.Semaphore()

BASE_URL = 'https://onlinejudge.org/'
MAX_THREADS = 10


def get_soup(url):
    html = urllib.request.urlopen(url).read()
    return BeautifulSoup(html, 'html.parser')


def isProblemCategory(tag):
    try:
        return 'sectiontableentry' in tag['class'][0]
    except:
        return False


def getProblemsCategory(soup):
    return list(filter(lambda tag: isProblemCategory(tag),
                       soup.find_all('tr')))


links_set = set()


def getCategoryLinks(soup):
    link_list = []
    categories = getProblemsCategory(soup)
    for category in categories:
        for tag in category.find_all('a'):
            try:
                link = tag['href']
                if link not in links_set:
                    sem.acquire()
                    link_list.append(link)
                    links_set.add(link)
                    sem.release()
            except:
                pass
    return link_list


links = ['index.php?option=com_onlinejudge&Itemid=8']
threads = []


def processLink(url, links):
    soup = get_soup(url)
    otherLinks = getCategoryLinks(soup)
    sem.acquire()
    links += otherLinks
    sem.release()


while len(links) > 0:
    selected_link = links.pop(0)
    if 'https://www.udebug.com/UVa' in selected_link:
        continue
    if 'page=show_problem' in selected_link:
        print(selected_link)
        continue
    url = BASE_URL + selected_link

    t = threading.Thread(target=processLink, args=(url, links))
    t.start()
    threads.append(t)
    if len(links) == 0 or len(threads) > MAX_THREADS:
        threads.pop(0).join()

for t in threads:
    t.join()