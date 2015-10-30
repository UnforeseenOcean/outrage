import urllib
import time
import os
from bs4 import BeautifulSoup
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.manager.showWhenStarting",False)
fp.set_preference("browser.download.dir", os.getcwd())
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4")
driver = webdriver.Firefox(firefox_profile=fp)

start_page = 80
pages = 140
base =  'https://www.dvidshub.net'
start = base + '/video/category/greetings/page/'


def login():
    print 'logging in'
    driver.get("https://www.dvidshub.net/login")

    elem = driver.find_element_by_name("email")
    elem.send_keys("dvids@mailinator.com")

    elem = driver.find_element_by_name("password")
    elem.send_keys("whatever")

    elem.submit()


def save_file(url):
    print 'downloading', url
    driver.get(url)

# def save_file(url, filename):
#     print 'downloading', url, 'to', filename
#     r = requests.get(url, stream=True, cookies=cookies)
#     print r.text
#     print r.status_code
#     if r.status_code == 200:
#         with open(filename, 'wb') as f:
#             r.raw.decode_content = True
#             shutil.copyfileobj(r.raw, f)

def download(url):
    try:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")

        el = soup.find('td', text='1920x1080')

        if el:
            link = el.parent.select('a')[0].get('href')
            link = 'https://www.dvidshub.net' + link
            save_file(link)

        # filename = 'greetings/' + link.split('/')[-1]
        #
        # if filename.endswith('.mp4') is False:
        #     filename = filename + '.mp4'
        #
        # if os.path.exists(filename) is False:
        #     save_file(link, filename)
        #     time.sleep(1)

    except Exception as e:
        print 'failed', url, e
        return False


def main():
    login()
    for i in range(start_page, pages):
        print 'page', str(i)
        indexurl = start + str(i)
        urls = []
        try:
            soup = BeautifulSoup(urllib.urlopen(indexurl).read(), "html.parser")
            urls = [base + a.get('href') for a in soup.select('#video_thumbcontainer .left a')]
        except:
            print 'page', str(i), 'failed'
            continue
        for url in urls:
            vid_id = url.split('/')[-2]
            new_url = 'https://www.dvidshub.net/download/popup/' + vid_id
            download(new_url)
            time.sleep(.1)


if __name__ == "__main__":
    main()
    # download('https://www.dvidshub.net/download/popup/410633')
