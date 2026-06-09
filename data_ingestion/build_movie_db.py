"""
build_movie_db.py
─────────────────
Parses the 13,711 enriched movie .txt files (created by enrich_dataset.py)
and builds a compact JSON database for the recommendation website.

Uses:  dataset/movies/<Genre>/<movie_id>.txt  →  movie_recommender/movies_db.json

Each .txt file format (from enrich_dataset.py):
    Title

    Tagline

    Overview

    Director: Name

    Cast: Actor1 Actor2 Actor3

    Keywords: kw1 kw2 kw3
    kw1 kw2 kw3        ← repeated twice for TF-IDF weight
    kw1 kw2 kw3
"""

import os, json, re

# ── Paths ──────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE, "dataset", "movies")
OUT_DIR = os.path.join(BASE, "movie_recommender")
OUT_JSON = os.path.join(OUT_DIR, "movies_db.json")

os.makedirs(OUT_DIR, exist_ok=True)

# ── Genre config ────────────────────────────────────────────
# Keep ALL genres but cap per-genre to keep JSON < 5MB
MAX_PER_GENRE = 200   # ~200 × 17 genres ≈ 3,400 movies

# ── Parser ──────────────────────────────────────────────────
def parse_txt(path: str, movie_id: str, genre: str) -> dict:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            raw = f.read()
    except Exception:
        return None

    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    if not blocks:
        return None

    title    = blocks[0]
    tagline  = ""
    overview = ""
    director = ""
    cast     = []
    keywords = []

    for block in blocks[1:]:
        lo = block.lower()
        if block.startswith("Director:"):
            director = block[9:].strip()
        elif block.startswith("Cast:"):
            raw_cast = block[5:].strip()
            # Cast members are space-separated (names joined without commas)
            # Try to split by common name patterns
            cast = raw_cast.split()[:6]  # just words; good enough for matching
        elif block.startswith("Keywords:"):
            kw_raw = block[9:].strip()
            keywords = list(dict.fromkeys(kw_raw.split()))  # unique, preserve order
        elif block.startswith("kw") or re.match(r'^[a-z]', block) and 0 < len(block) < 400 and len(block.split()) > 3:
            # repeated keyword block — skip
            pass
        elif not tagline and len(block) < 200 and "\n" not in block:
            tagline = block
        elif not overview:
            overview = block

    if not title:
        return None

    return {
        "id":  int(movie_id) if movie_id.isdigit() else movie_id,
        "t":   title[:120],                   # title
        "g":   genre,                         # genre (Mahout label)
        "tl":  tagline[:150] if tagline else "",
        "ov":  overview[:400] if overview else "",
        "d":   director[:60]  if director else "",
        "c":   cast[:5],                      # top 5 cast words
        "kw":  keywords[:30],                 # top 30 keywords
    }

# ── Main ────────────────────────────────────────────────────
def main():
    movies   = []
    by_genre = {}

    print("=" * 60)
    print(" Building movies_db.json from enriched dataset")
    print("=" * 60)

    genre_dirs = sorted([
        d for d in os.scandir(DATASET) if d.is_dir()
    ], key=lambda d: d.name)

    for gdir in genre_dirs:
        genre = gdir.name
        files = sorted(
            [f for f in os.scandir(gdir.path) if f.name.endswith(".txt")],
            key=lambda f: -f.stat().st_size    # richest files first
        )[:MAX_PER_GENRE]

        count = 0
        by_genre[genre] = []

        for f in files:
            movie_id = f.name.replace(".txt", "")
            m = parse_txt(f.path, movie_id, genre)
            if m:
                movies.append(m)
                by_genre[genre].append(m["id"])
                count += 1

        print(f"  {genre:<20} {count:>4} movies")

    # ── Genre metadata ──────────────────────────────────────
    genres_meta = [
        {"name": g, "ids": ids, "count": len(ids)}
        for g, ids in by_genre.items() if ids
    ]

    db = {"movies": movies, "genres": genres_meta}

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(db, f, separators=(",", ":"), ensure_ascii=False)

    size_mb = os.path.getsize(OUT_JSON) / 1_048_576
    print(f"\n{'-'*60}")
    print(f" Total movies : {len(movies)}")
    print(f" Genres       : {len(genres_meta)}")
    print(f" Output size  : {size_mb:.2f} MB")
    print(f" Saved to     : {OUT_JSON}")
    print(f"{'-'*60}")

if __name__ == "__main__":
    main()
