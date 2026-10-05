# App Store & Google Play reviews scraper in Python: export iOS and Android app reviews to JSON/CSV

A short tutorial for pulling **App Store reviews** and **Google Play reviews** (star rating, title, full text, date, app version, helpful votes and the developer's reply, plus app metadata on every row) into Python with the [App Store & Google Play Reviews Scraper](https://apify.com/rel8ble/app-reviews-scraper) on Apify. Both stores come back in one unified table, so you can compare an app's iOS and Android feedback without writing two scrapers. Useful as an **app reviews API** for reputation monitoring, competitor research, ASO and sentiment analysis.

> Disclosure: I built this actor; it's a paid tool on Apify ($0.25 per 1,000 reviews). The code in this repo is MIT-licensed.

## How it works

Paste App Store or Google Play URLs, or bare IDs (`324684580`, `com.spotify.music`), mixed freely. The actor reads each store's public web data over plain HTTP (no headless browser, no login) and pages through as many reviews as the store serves, not just the first 500. In testing it saved 20,000 reviews in under 30 seconds. Filters (`stars`, `reviewsSince`) run before charging, so you only pay for reviews you keep.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/app-reviews-scraper").call(run_input={
    "apps": [
        "https://apps.apple.com/us/app/spotify-music-and-podcasts/id324684580",
        "com.spotify.music",
    ],
    "country": "us",
    "sort": "newest",
    "maxReviewsPerApp": 50,
})

for r in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(r["store"], r["rating"], r["reviewDate"][:10], (r["text"] or "")[:80])
```

[`example.py`](example.py) is the runnable version: it pulls the last 30 days of 1-2 star complaints for one app on both stores, prints the average rating, developer-reply rate and most-complained app versions per store, and writes everything to `complaints.csv`.

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/app-reviews-scraper').call({
    apps: ['com.duolingo'], country: 'us', stars: [1, 2], maxReviewsPerApp: 100,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.map((r) => `${r.rating} stars, v${r.version}: ${r.text}`));
```

## Input

| Field | Default | What it does |
|---|---|---|
| `apps` | Spotify on both stores | App Store or Google Play URLs or IDs, one per line, both stores mixed |
| `country` | `us` | 2-letter store country (`us`, `gb`, `de`, `jp`, `br` ...); each country has its own reviews |
| `language` | `en` | Google Play only: review language (`en`, `de`, `es`, `ja` ...) |
| `sort` | `newest` | `newest`, `mostHelpful`, `mostFavorable`, `mostCritical` |
| `maxReviewsPerApp` | 100 | Stop each app after this many reviews; `0` = everything the store pages through |
| `stars` | all | e.g. `[1, 2]` to keep only complaints (filtered-out reviews are free) |
| `reviewsSince` | - | `YYYY-MM-DD`; with `sort: newest` the run stops at the first older review |

## Output sample

One row per review, same field names on both stores (fields a store doesn't have are `null`). Real rows from a test run, trimmed:

```json
[
  {
    "store": "appStore",
    "appId": "324684580",
    "appName": "Spotify: Music and Podcasts",
    "country": "us",
    "rating": 1,
    "title": "Ads",
    "text": "screw you",
    "reviewDate": "2026-09-22T22:36:00.000Z",
    "version": null,
    "thumbsUp": 0,
    "isEdited": true,
    "developerReply": "Hey! We hear you and we'll pass your feedback along to the Ads team. ...",
    "developerReplyDate": "2026-09-16T13:55:16.000Z",
    "appRating": 4.77,
    "appRatingCount": 42231119,
    "appVersion": "9.1.84",
    "appGenre": "Music"
  },
  {
    "store": "googlePlay",
    "appId": "com.duolingo",
    "appName": "Duolingo: Language Lessons",
    "country": "us",
    "language": "en",
    "rating": 4,
    "title": null,
    "text": "very user friendly",
    "reviewDate": "2026-09-10T20:31:09.000Z",
    "version": "6.95.4",
    "thumbsUp": 2,
    "developerReply": null,
    "appRating": 4.73,
    "appRatingCount": 49102784,
    "appReviewCount": 956943,
    "appInstalls": "500,000,000+",
    "appGenre": "Education"
  }
]
```

## Price

Pay per result: **$0.25 per 1,000 reviews** (10,000 reviews = $2.50). No start fee; reviews dropped by your filters and apps that don't exist are free. The Apify free plan's $5 monthly credit covers about 20,000 reviews.

## Limits

- App Store reviews carry no app version (`version` is `null`); Google Play rows have it for about 85% of reviews.
- Google Play returns one review language per run; run twice for two languages.
- Reviews are per country: `us` and `gb` are different sets, so run each country separately.
- Google Play has no "most critical" order; the actor walks 1-star, then 2-star, newest first within each.
- Reviewer names and avatars are personal data under GDPR/CCPA; have a lawful basis before storing them.

## Links

- Actor on the Apify Store: https://apify.com/rel8ble/app-reviews-scraper
- apify-client for Python: https://docs.apify.com/api/client/python

## License

MIT, see [LICENSE](LICENSE).
