from bs4 import BeautifulSoup
import feedparser
import requests
import time

URL_ROOT = 'https://las.leagueoflegends.com/es'
WEBHOOK_URL = "https://discordapp.com/api/webhooks/0000000000000/00000000000000000000000000000"

# etag = ""
# modified = ""
guids = {}

def fetch_data():
	global URL_ROOT, guids, etag, modified
	feed = feedparser.parse(URL_ROOT+'/rss.xml')
	# etag = feed.etag
	# modified = feed.modified

	for entry in feed.entries:
		guid = entry.guid.split(" ")[0]
		guids[guid] = True

def check_for_new_articles():
	# global URL_ROOT, guids, etag, modified
	global URL_ROOT, guids
	# feed = feedparser.parse(URL_ROOT+'/rss.xml', etag=etag, modified=modified)
	feed = feedparser.parse(URL_ROOT+'/rss.xml')
	if feed.status == 200:
		for entry in feed.entries:
			try:
				entry_guid = entry.guid.split(" ")[0]
			except:
				continue
			if entry_guid not in guids:
				soup = BeautifulSoup(entry.description, "html.parser")
				description = soup.find('div').getText()
				image_url = URL_ROOT+soup.find('img')['src']
				
				post_to_discord(entry.title, description, entry.link, image_url, entry.published_parsed)

				guids[entry_guid] = True
	# etag = feed.etag
	# modified = feed.modified

def post_to_discord(title, description, link, image, date):
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
		        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', date)
		    }
		]
	}
	print ("Posting to Discord...")
	r = requests.post(WEBHOOK_URL, json=payload, headers={'Content-Type': 'multipart/form-data'})
	print ("HTTP REQUEST: ", r.status_code, r.text)

if __name__ == '__main__':	
	print ("Fetching data from League of Legends' servers...")
	fetch_data()
	print ("Listening for new articles!")
	while True:
		check_for_new_articles()
		time.sleep(10)