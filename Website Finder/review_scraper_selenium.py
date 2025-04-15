import os
import csv
import json
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options)

# --- Output folder ---
output_dir = os.path.join(os.path.dirname(__file__), "reddit_posts")
os.makedirs(output_dir, exist_ok=True)

def parse_comment_block(comment_div):
    comment = {}

    # Author
    try:
        author_elem = comment_div.find_element(By.CSS_SELECTOR, 'a[href^="/user/"]')
        comment['author'] = author_elem.text.strip()
    except:
        comment['author'] = "N/A"

    # Timestamp
    try:
        time_elem = comment_div.find_element(By.CSS_SELECTOR, 'a[data-click-id="timestamp"]')
        comment['timestamp'] = time_elem.text.strip()
    except:
        comment['timestamp'] = "N/A"

    # Body
    try:
        body_elem = comment_div.find_element(By.CSS_SELECTOR, 'div._1qeIAgB0cPwnLhDF9XSiJM')
        comment['body'] = body_elem.text.strip()
    except:
        comment['body'] = "N/A"

    # Replies (recursive)
    comment['replies'] = []
    try:
        nested_comments = comment_div.find_elements(By.CSS_SELECTOR, "div._3tw__eCCe7j-epNCKGXUKk")
        for child in nested_comments:
            if child != comment_div:
                comment['replies'].append(parse_comment_block(child))
    except:
        pass

    return comment


def extract_post_id(url):
    parts = urlparse(url).path.split('/')
    return parts[2], parts[4]  # subreddit, post_id

def scrape_post(url):
    driver.get(url)
    print(f"Attempting to get comments from page: {url}")
    try:
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div._3tw__eCCe7j-epNCKGXUKk"))

    )
    except:
        print("ERROR: Comments not found after 10 seconds")
    
    print(driver.page_source)
    subreddit, post_id = extract_post_id(url)

    # --- Title ---
    try:
        title_elem = driver.find_element(By.CSS_SELECTOR, "h1[data-test-id='post-title']")
        title = title_elem.text.strip()
    except:
        title = "N/A"

    # --- Post body ---
    try:
        body_elem = driver.find_element(By.CSS_SELECTOR, "div[data-test-id='post-content']")
        post_body = body_elem.text.strip()
    except:
        post_body = "N/A"

    # --- Author ---
    try:
        author_elem = driver.find_element(By.CSS_SELECTOR, "a[data-click-id='user']")
        author = author_elem.text.strip()
    except:
        author = "N/A"

    # --- Comments (only top-level) ---
    comments = []
    try:
        for i in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        comment_blocks = driver.find_elements(By.CSS_SELECTOR, "div._3tw__eCCe7j-epNCKGXUKk")
        print(f"Found {len(comment_blocks)} comment blocks")

        for block in comment_blocks:
            parent = block.find_element(By.XPATH, "..")
            if "comment" not in parent.get_attribute("outerHTML"):
                comment_data = parse_comment_block(block)
                comments.append(comment_data)
    except Exception as e:
        print(f"Error extracting comments: {e}")

    return {
        "url": url,
        "title": title,
        "subreddit": subreddit,
        "author": author,
        "post_body": post_body,
        "timestamp": "N/A",
        "comments": comments
    }


# --- Main loop: read CSV ---
csv_path = os.path.join(os.path.dirname(__file__), "reddit_age_verification_links.csv")
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
