import requests
from bs4 import BeautifulSoup
import csv, time, os, urllib.parse, re

# \s+ (one or more whitespace characters), ? (optional preceding character)

regex_patterns = [
    r"age\s+verification",
    r"(no|alternative|fake|lying)\s+age\s+verification",
    r"yoti\s+verification",
    r"(onlyfans|tiktok|youtube|discord)\s+age\s+verification",
    r"(age\s+verification|verification\s+age)\s+(teenagers|minors)",
    r"(age\s+verification|verification\s+age)\s+policy",
    r"underage\s+users?\s+(age\s+verification|verification\s+age)",
    r"(age\s+verification|verification\s+age)\s+methods?",
    r"escape\s+(age\s+verification|verification\s+age)",
    r"(age\s+verification|verification\s+age)\s+bypass",
    r"(ID\s+age|AI\s+age|biometric\s+age)\s+verification",
    r"(age\s+verification|verification\s+age)\s+technology",
    r"(age\s+verification|verification\s+age)\s+solutions?",
    r"get\s+around\s+(age\s+verification|verification\s+age)",
    r"avoiding\s+(age\s+verification|verification\s+age)",
    r"(age\s+verification|verification\s+age)\s+loopholes?",
    r"(age\s+verification|verification\s+age)\s+workaround?",
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

# Function to search Reddit for posts related to the regex patterns
# and return the titles and URLs of the posts that match the patterns in the title or body.
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

def create_csv():
    all_results = []
    seen_urls = set()

    for pattern in regex_patterns:
        posts = search_reddit(pattern)
        for post in posts:
                if post["url"] not in seen_urls:
                    all_results.append(post)
                    seen_urls.add(post["url"])
        time.sleep(2)

    output_file = os.path.join(os.path.dirname(__file__), "reddit_age_veri_broad.csv")
    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url"])
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nResults saved to {output_file}")


def remove_dups():
    dir_path = os.getcwd()
    file_dir = os.path.join(dir_path, 'Qualitative Work', 'reddit_posts.csv')
    output_csv = "reddit_posts.csv"
    
    with open(file_dir, 'r', encoding='utf-8') as in_file, open(output_csv, 'w', encoding='utf-8') as out_file:
        seen = set() # set for fast O(1) amortized lookup
        for line in in_file:
            if line in seen: continue # skip duplicate

            seen.add(line)
            out_file.write(line)

remove_dups()