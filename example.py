"""Pull the last 30 days of 1-2 star complaints for one app on the App Store and
Google Play, summarise them per store, and save them to complaints.csv.

Usage:
    pip install -r requirements.txt
    APIFY_TOKEN=<YOUR_APIFY_TOKEN> python example.py
"""
import csv
import os
from collections import Counter, defaultdict
from datetime import date, timedelta

from apify_client import ApifyClient

TOKEN = os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>")
APPS = [
    "https://apps.apple.com/us/app/duolingo-language-lessons/id570060128",
    "com.duolingo",
]
SINCE = (date.today() - timedelta(days=30)).isoformat()

client = ApifyClient(TOKEN)
run = client.actor("rel8ble/app-reviews-scraper").call(run_input={
    "apps": APPS,
    "country": "us",
    "language": "en",
    "sort": "newest",
    "stars": [1, 2],
    "reviewsSince": SINCE,
    "maxReviewsPerApp": 200,
})

reviews = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"{len(reviews)} complaints (1-2 stars) since {SINCE}\n")

by_store = defaultdict(list)
for r in reviews:
    by_store[r["store"]].append(r)

for store, rows in by_store.items():
    replied = sum(1 for r in rows if r.get("developerReply"))
    avg = sum(r["rating"] for r in rows) / len(rows)
    print(f"{store}: {len(rows)} reviews, avg {avg:.2f} stars, "
          f"developer replied to {replied} ({replied / len(rows):.0%})")
    versions = Counter(r["version"] for r in rows if r.get("version"))
    if versions:
        top = ", ".join(f"{v} ({n})" for v, n in versions.most_common(3))
        print(f"  most-complained versions: {top}")

fields = ["store", "appName", "rating", "reviewDate", "version", "title", "text",
          "thumbsUp", "developerReply", "reviewUrl"]
with open("complaints.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(reviews)
print("\nSaved complaints.csv")
