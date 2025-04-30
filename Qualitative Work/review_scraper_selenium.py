import os
import csv
import json
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options)

# --- Output folder ---
output_dir = os.path.join(os.path.dirname(__file__), "reddit_posts_new")
os.makedirs(output_dir, exist_ok=True)

def extract_post_id(url):
    parts = urlparse(url).path.split('/')
    return parts[2], parts[4]  # subreddit, post_id

def scrape_post(url):
    driver.get(url)
    print(f"Attempting to get comments from page: {url}")
    time.sleep(5)  # Wait for the page to load
    
    html = driver.page_source
    # print(html) 
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.prettify())

    subreddit, post_id = extract_post_id(url)

    # --- Title, Author, Body of Post ---
    title_tag = soup.find('h1', {'slot': 'title'})
    title = title_tag.get_text(strip=True) if title_tag else 'N/A'

    post_tag = soup.find('shreddit-post')
    post_author = post_tag.get('user-id', 'N/A') if post_tag else 'N/A'

    text_body_wrapper = soup.find('div', {'slot': 'text-body'})
    post_body = ''
    if text_body_wrapper:
        paragraphs = text_body_wrapper.find_all('p')
        post_body = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
    # --- Comments (only top-level) ---
    comments = []
    
    shreddit_comments = soup.find_all("shreddit-comment")
    print(f"Found {len(shreddit_comments)} comment blocks")


    for comment in shreddit_comments:
        author = comment.get('author', 'N/A')
        timestamp = comment.get('aria-label', '').replace('Comment from ', '')
        
        # Find the inner comment text
        body_tag = comment.find('div', attrs={'slot': 'comment'})
        if body_tag:
            comment_text = body_tag.get_text(strip=True)
        else:
            comment_text = "N/A"
        
        comments.append({
            "author": author,
            "timestamp": timestamp,
            "body": comment_text
        })
    

    return {
        "subreddit": subreddit,
        "post_id": post_id,
        "title": title,
        "body": post_body,
        "author": author,
        "comments": comments
    }


# --- Main loop: read CSV ---
csv_path = os.path.join(os.path.dirname(__file__), "reddit_posts.csv")
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        url = row["url"]
        print(f"Scraping: {url}")
        try:
            data = scrape_post(url)
            filename = f"post_{data['subreddit']}_{extract_post_id(url)[1]}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        time.sleep(5)  # Be kind to Reddit

# --- Done ---
driver.quit()
print(f"\nDone scraping. Files saved to: {output_dir}")
