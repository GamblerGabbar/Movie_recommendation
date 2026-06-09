"""
enrich_dataset.py
Enriches existing movie .txt files with:
  - Tagline (very genre-specific short phrase)
  - Keywords (curated TMDB genre tags e.g. "zombie", "heist", "space travel")
  - Cast (top 3 actors - many actors are genre-specific)
  - Director
All fetched via /movie/{id}?append_to_response=keywords,credits
One API call per movie. Rewrites files in-place.
"""
import os
import re
import requests
import time
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not set in .env")

BASE_URL  = "https://api.themoviedb.org/3"
DATASET   = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "movies")

def api_get(url, retries=5):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                print(f"    Rate-limited — waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            wait = 2 ** attempt
            print(f"    Error attempt {attempt+1}: {e} — retry in {wait}s", flush=True)
            time.sleep(wait)
    return None

def enrich_file(filepath, movie_id):
    """Fetch rich metadata and rewrite the file."""
    url = (f"{BASE_URL}/movie/{movie_id}"
           f"?api_key={TMDB_API_KEY}&language=en-US"
           f"&append_to_response=keywords,credits")
    data = api_get(url)
    if not data:
        return False

    title    = (data.get('title') or '').strip()
    overview = (data.get('overview') or '').strip()
    tagline  = (data.get('tagline') or '').strip()

    # Keywords — curated TMDB tags, extremely genre-discriminative
    kw_list  = [k['name'] for k in data.get('keywords', {}).get('keywords', [])]
    keywords = ' '.join(kw_list)  # treat as additional text tokens

    # Top 3 cast members (actors are strongly genre-associated)
    cast_raw = data.get('credits', {}).get('cast', [])[:3]
    cast     = ' '.join([c.get('name', '') for c in cast_raw])

    # Director
    crew_raw = data.get('credits', {}).get('crew', [])
    director = next((c.get('name', '') for c in crew_raw if c.get('job') == 'Director'), '')

    # Build enriched content — repeat keywords 3× to boost their weight in TF-IDF
    parts = [title]
    if tagline:
        parts.append(tagline)
    if overview:
        parts.append(overview)
    if director:
        parts.append(f"Director: {director}")
    if cast:
        parts.append(f"Cast: {cast}")
    if keywords:
        # Repeat keywords to give them more TF-IDF weight
        parts.append(f"Keywords: {keywords}")
        parts.append(keywords)
        parts.append(keywords)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(parts))
    return True


if __name__ == '__main__':
    # Collect all movie files
    all_files = []
    for genre_dir in os.scandir(DATASET):
        if genre_dir.is_dir():
            for movie_file in os.scandir(genre_dir.path):
                if movie_file.name.endswith('.txt'):
                    movie_id = movie_file.name.replace('.txt', '')
                    all_files.append((movie_file.path, movie_id))

    total    = len(all_files)
    enriched = 0
    failed   = 0

    print(f"{'='*60}", flush=True)
    print(f" Enriching {total} movie files with keywords + cast + tagline", flush=True)
    print(f"{'='*60}", flush=True)

    for i, (filepath, movie_id) in enumerate(all_files, 1):
        ok = enrich_file(filepath, movie_id)
        if ok:
            enriched += 1
        else:
            failed += 1

        if i % 250 == 0 or i == 1 or i == total:
            print(f"  [{i:>5}/{total}] enriched={enriched}  failed={failed}", flush=True)

        time.sleep(0.27)   # ~40 req/10s polite rate limit

    print(f"\n{'='*60}", flush=True)
    print(f" DONE — enriched {enriched}/{total} files  ({failed} failed)", flush=True)
    print(f"{'='*60}", flush=True)
