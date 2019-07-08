######################################################
 # Copyright (C) 2018 Tomás Caram <aresmta@gmail.com>
 # 
 # Released under the MIT License
 # Refer to the LICENSE file for more information
 # Written by Tomás Caram <aresmta@gmail.com>, August 2018
#######################################################

from bs4 import BeautifulSoup
import feedparser
import requests
import time
import json

DATA = {}

guids = {}
titles = {}

def fetch_data():
    global guids, titles
    for server in DATA['SERVERS']:
        url = DATA['SERVERS'][server]['url'] 
        lang = DATA['SERVERS'][server]['lang'] 

        feed = feedparser.parse(url+lang+"/rss.xml")
        for entry in feed.entries:
            guid = entry.guid.split(" ")[0]
            title = entry.title

            guids[guid] = True
            titles[title] = True

def check_for_new_articles():
    global guids, titles
    for server in DATA['SERVERS']:
        server_name = DATA['SERVERS'][server]['name']
        url = DATA['SERVERS'][server]['url']
        nurl = url[:-1]
        lang = DATA['SERVERS'][server]['lang'] 

        feed = feedparser.parse(url+lang+"/rss.xml")
        if feed.status == 200:
            for entry in feed.entries:
                try:
                    entry_guid = entry.guid.split(" ")[0]
                except:
                    continue
                if entry_guid not in guids and not entry.title in titles:
                    title = entry.title
                    soup = BeautifulSoup(entry.description, "html.parser")
                    description = soup.find('div').getText()
                    image_url = nurl+soup.find('img')['src']
                    
                    post_to_discord(title, description, entry.link, image_url, entry.published_parsed, server_name)

                    guids[entry_guid] = True
                    titles[title] = True

def post_to_discord(title, description, link, image, date, server_name):
    payload = {
        "username": "Quinn",
        "avatar_url": "http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/Quinn.png",
        "content": "",
        "embeds": [
            {
                "title": title,
                "description": description,
                "url": link,
                "image": {"url": image},
                "color": 15258703,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', date),
                "footer": {"text": server_name}
            }
        ]
    }
    print ("Posting to Discord...")
    for webhook in DATA['WEBHOOK_URL']:
    	r = requests.post(webhook, json=payload, headers={'Content-Type': 'multipart/form-data'})
    	print ("HTTP REQUEST: ", r.status_code, r.text)

if __name__ == '__main__':
    print ("Reading from config file")
    with open('config/config.json') as cfg:
        DATA = json.load(cfg)
    print ("Fetching data from League of Legends' servers...")
    fetch_data()
    print ("Listening for new articles!")
    while True:
        check_for_new_articles()
        time.sleep(10)