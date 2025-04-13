import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import urllib.parse

keywords = [
    "age verification",
    "age verification teenagers",
    "age verification minors",
    "age verification policy",
    "underage users age verification",
    "age verification methods",
    "escape age verification",
    "age verification bypass",
    "ID verification",
    "age verification technology",
    "age verification solutions",
    "get around age verification",
    "avoiding age verification",
    "age verification loopholes",
]

headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Function to search Reddit for posts related to the keywords
# and return the titles and URLs of the posts that contain the keywords in the title or body.
def search_reddit(query):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.reddit.com/search/?q={encoded_query}&sort=relevance&t=all"

    print(f"Searching: {query}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith("/r/") and "/comments/" in href:
            title = link.text.strip()
            full_url = "https://www.reddit.com" + href
            results.append({
                "title": title,
                "url": full_url
            })

    return results

all_results = []
seen_urls = set()

for keyword in keywords:
    posts = search_reddit(keyword)
    for post in posts:
        if post["url"] not in seen_urls:
            all_results.append(post)
            seen_urls.add(post["url"])
    time.sleep(2) 

output_file = os.path.join(os.path.dirname(__file__), "reddit_age_verification_links.csv")
with open(output_file, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["title", "url"])
    writer.writeheader()
    writer.writerows(all_results)

print(f"\nSaved {len(all_results)} posts to reddit_age_verification_links.csv")
