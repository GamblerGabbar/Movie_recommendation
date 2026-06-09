import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY is not set in the .env file")

BASE_URL   = "https://api.themoviedb.org/3"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "movies")

# All TMDB paginated endpoints; (label, path, max_pages)
ENDPOINTS = [
    ("popular",     "/movie/popular",     500),
    ("top_rated",   "/movie/top_rated",   500),
    ("now_playing", "/movie/now_playing",  50),
    ("upcoming",    "/movie/upcoming",     50),
]


def api_get(url, retries=5):
    """GET with exponential-backoff retry."""
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"  Rate-limited — waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            if r.status_code == 200:
                return r.json()
            print(f"  HTTP {r.status_code}", flush=True)
        except Exception as e:
            wait = 2 ** attempt
            print(f"  Error (attempt {attempt+1}): {e}  retrying in {wait}s", flush=True)
            time.sleep(wait)
    return None


def fetch_genres():
    data = api_get(f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US")
    if not data:
        raise RuntimeError("Failed to fetch genres.")
    return {g['id']: g['name'] for g in data.get('genres', [])}


def save_movie(genres_map, movie):
    """Save a single movie immediately to disk. Returns True if saved."""
    mid      = movie.get('id')
    title    = (movie.get('title') or '').strip()
    overview = (movie.get('overview') or '').strip()
    gids     = movie.get('genre_ids', [])

    if not overview or not gids:
        return False
    genre_name = genres_map.get(gids[0])
    if not genre_name:
        return False

    folder    = genre_name.replace(" ", "_")
    genre_dir = os.path.join(OUTPUT_DIR, folder)
    os.makedirs(genre_dir, exist_ok=True)

    filepath = os.path.join(genre_dir, f"{mid}.txt")
    if os.path.exists(filepath):          # already saved in a previous run
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n{overview}")
    return True


if __name__ == "__main__":
    print("=" * 60, flush=True)
    print(" TMDB Maximum Fetch — All Endpoints (incremental save)", flush=True)
    print("=" * 60, flush=True)

    print("\nFetching genre definitions...", flush=True)
    genres = fetch_genres()
    print(f"  Found {len(genres)} genres.", flush=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    seen_ids  = set()
    total_saved = 0

    for label, endpoint, max_pages in ENDPOINTS:
        print(f"\n{'='*50}", flush=True)
        print(f"[{label}] — up to {max_pages} pages", flush=True)
        endpoint_saved = 0

        for page in range(1, max_pages + 1):
            url  = (f"{BASE_URL}{endpoint}"
                    f"?api_key={TMDB_API_KEY}&language=en-US&page={page}")
            data = api_get(url)
            if data is None:
                print(f"  Skipping page {page} (failed after retries)", flush=True)
                continue

            results  = data.get('results', [])
            total_pg = data.get('total_pages', 1)

            page_saved = 0
            for movie in results:
                mid = movie.get('id')
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)
                if save_movie(genres, movie):
                    page_saved     += 1
                    endpoint_saved += 1
                    total_saved    += 1

            if page % 25 == 0 or page == 1:
                print(
                    f"  [{label}] page {page:>3}/{min(max_pages,total_pg):<3} "
                    f"| this page +{page_saved:>2} "
                    f"| endpoint total {endpoint_saved:>4} "
                    f"| grand total {total_saved:>5}",
                    flush=True
                )

            # Stop if TMDB says there are no more pages
            if page >= total_pg:
                print(f"  [{label}] last page reached ({total_pg})", flush=True)
                break

            time.sleep(0.27)   # ~40 req/10s polite cap

        print(f"[{label}] done — saved {endpoint_saved} new movies", flush=True)

    print(f"""
{'='*60}
 FETCH COMPLETE
   Total movies saved : {total_saved}
   Dataset location   : {OUTPUT_DIR}
{'='*60}""", flush=True)
