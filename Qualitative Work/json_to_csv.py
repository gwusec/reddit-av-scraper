import os,json,csv

dir_path = os.getcwd()
file_dir = os.path.join(dir_path, 'Qualitative Work', 'reddit_posts')
output_csv = "reddit_comments.csv"


all_comments = [] # comments


for filename in os.listdir(file_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(file_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            post_id = data.get("post_id", "N/A") # post id or none
            subreddit = data.get("subreddit", "N/A") # subreddit or none
            for comment in data.get("comments", []):
                all_comments.append({
                    "post_id": post_id,
                    "subreddit": subreddit,
                    "author": comment.get("author", "N/A"),
                    "body": comment.get("body", "N/A")
                })


with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["post_id", "subreddit", "author", "body"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_comments)