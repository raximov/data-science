import csv
import datetime
import re
import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import functools
from collections import defaultdict, Counter


def _resolve_path(path):
    """Resolve path relative to this script if it looks like a default relative path."""
    if not os.path.isabs(path) and ".." in path:
        base = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(base) == "src":
            return os.path.abspath(os.path.join(base, path))
    return os.path.abspath(path)


def _load_csv(path, limit=1000):
    """Load up to `limit` data rows (excluding header) from a CSV file."""
    path = _resolve_path(path)
    rows = []
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)
    return rows


def _load_movies_map(movies_path, limit=None):
    """Return dict {movieId_str -> title} from movies.csv (no row limit by default)."""
    movies_path = _resolve_path(movies_path)
    mapping = {}
    if not os.path.exists(movies_path):
        return mapping
    with open(movies_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit is not None and i >= limit:
                break
            mapping[row["movieId"]] = row["title"]
    return mapping


# ---------------------------------------------------------------------------
# Movies
# ---------------------------------------------------------------------------

class Movies:
    """Analyzing data from movies.csv.

    Dataset schema: movieId, title, genres
    Title format:   "Some Title (YYYY)"
    Genres format:  "Genre1|Genre2|..." or "(no genres listed)"
    Uses first 1000 rows.
    """

    def __init__(self, path_to_the_file):
        self.path = path_to_the_file
        self.rows = _load_csv(self.path, limit=1000)

    def dist_by_release(self):
        """Return dict {year(int) -> count} sorted by count descending."""
        counts = defaultdict(int)
        for row in self.rows:
            m = re.search(r"\((\d{4})\)", row.get("title", ""))
            if m:
                counts[int(m.group(1))] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def dist_by_genres(self):
        """Return dict {genre -> count} sorted by count descending."""
        counts = defaultdict(int)
        for row in self.rows:
            genres = row.get("genres", "")
            if genres and genres != "(no genres listed)":
                for g in genres.split("|"):
                    counts[g] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def most_genres(self, n):
        """Return dict {title -> genre_count} for top-n movies, sorted by count desc."""
        counts = {}
        for row in self.rows:
            genres = row.get("genres", "")
            if genres and genres != "(no genres listed)":
                cnt = len(genres.split("|"))
            else:
                cnt = 0
            counts[row.get("title", "")] = cnt
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------

class Ratings:
    """Analyzing data from ratings.csv.

    Dataset schema: userId, movieId, rating, timestamp
    Ratings are on a 5-star scale with 0.5 increments.
    Timestamps are seconds since UTC epoch.
    Uses first 1000 rows.

    Inner classes:
        Ratings.Movies  - analysis grouped by movie
        Ratings.Users   - analysis grouped by user
    """

    def __init__(self, path_to_the_file):
        self.path = path_to_the_file
        self.rows = _load_csv(self.path, limit=1000)

        for row in self.rows:
            row["rating"] = float(row["rating"])
            try:
                row["timestamp"] = int(row["timestamp"])
            except (ValueError, KeyError):
                row["timestamp"] = 0

        movies_path = os.path.join(os.path.dirname(self.path), "movies.csv")
        self._movies_map = {}
        if os.path.exists(movies_path):
            self._movies_map = _load_movies_map(movies_path)

        self.movies = self.Movies(self)
        self.users = self.Users(self)

    # ------------------------------------------------------------------
    class Movies:
        """Analysis of rating data grouped by movie."""

        def __init__(self, parent):
            self._p = parent

        def _title(self, movie_id):
            return self._p._movies_map.get(str(movie_id), str(movie_id))

        def dist_by_year(self):
            """Return {year(int) -> count} sorted by year ascending."""
            counts = defaultdict(int)
            for row in self._p.rows:
                try:
                    year = datetime.datetime.fromtimestamp(
                        row["timestamp"], datetime.timezone.utc
                    ).year
                except Exception:
                    continue
                counts[year] += 1
            return dict(sorted(counts.items(), key=lambda x: x[0]))

        def dist_by_rating(self):
            """Return {rating(float) -> count} sorted by rating ascending."""
            counts = defaultdict(int)
            for row in self._p.rows:
                counts[row["rating"]] += 1
            return dict(sorted(counts.items(), key=lambda x: x[0]))

        def top_by_num_of_ratings(self, n):
            """Return {title -> count} for top-n movies by number of ratings, desc."""
            counts = defaultdict(int)
            for row in self._p.rows:
                counts[self._title(row["movieId"])] += 1
            return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])

        def top_by_ratings(self, n, metric="average"):
            """Return {title -> value} for top-n movies by average or median rating."""
            by_movie = defaultdict(list)
            for row in self._p.rows:
                by_movie[self._title(row["movieId"])].append(row["rating"])

            results = {}
            for title, ratings in by_movie.items():
                if not ratings:
                    continue
                if metric == "median":
                    s = sorted(ratings)
                    l = len(s)
                    val = s[l // 2] if l % 2 == 1 else (s[l // 2 - 1] + s[l // 2]) / 2
                else:
                    val = sum(ratings) / len(ratings)
                results[title] = round(val, 2)

            return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])

        def top_controversial(self, n):
            """Return {title -> variance} for top-n movies by rating variance, desc."""
            by_movie = defaultdict(list)
            for row in self._p.rows:
                by_movie[self._title(row["movieId"])].append(row["rating"])

            results = {}
            for title, ratings in by_movie.items():
                if not ratings:
                    results[title] = 0.0
                    continue
                mean = sum(ratings) / len(ratings)
                var = sum((r - mean) ** 2 for r in ratings) / len(ratings)
                results[title] = round(var, 2)

            return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])

    # ------------------------------------------------------------------
    class Users(Movies):
        """Analysis of rating data grouped by user."""

        def __init__(self, parent):
            self._p = parent

        def _key(self, row):
            return int(row["userId"])

        def dist_by_ratings_number(self):
            """Return {num_ratings -> user_count} sorted by num_ratings ascending."""
            per_user = defaultdict(int)
            for row in self._p.rows:
                per_user[self._key(row)] += 1
            dist = defaultdict(int)
            for cnt in per_user.values():
                dist[cnt] += 1
            return dict(sorted(dist.items(), key=lambda x: x[0]))

        def dist_by_ratings_metric(self, metric="average"):
            """Return {rounded_metric -> user_count} sorted by metric ascending."""
            by_user = defaultdict(list)
            for row in self._p.rows:
                by_user[self._key(row)].append(row["rating"])

            dist = defaultdict(int)
            for uid, ratings in by_user.items():
                if not ratings:
                    continue
                if metric == "median":
                    s = sorted(ratings)
                    l = len(s)
                    val = s[l // 2] if l % 2 == 1 else (s[l // 2 - 1] + s[l // 2]) / 2
                else:
                    val = sum(ratings) / len(ratings)
                dist[round(val, 2)] += 1
            return dict(sorted(dist.items(), key=lambda x: x[0]))

        def top_controversial(self, n):
            """Return {userId -> variance} for top-n most controversial users, desc."""
            by_user = defaultdict(list)
            for row in self._p.rows:
                by_user[self._key(row)].append(row["rating"])

            results = {}
            for uid, ratings in by_user.items():
                if not ratings:
                    results[uid] = 0.0
                    continue
                mean = sum(ratings) / len(ratings)
                var = sum((r - mean) ** 2 for r in ratings) / len(ratings)
                results[uid] = round(var, 2)
            return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

class Tags:
    """Analyzing data from tags.csv.

    Dataset schema: userId, movieId, tag, timestamp
    Tags are free-text, user-generated.
    Uses first 1000 rows.
    """

    def __init__(self, path_to_the_file):
        self.path = path_to_the_file
        self.rows = _load_csv(self.path, limit=1000)

    def most_words(self, n):
        """Return {tag -> word_count} for top-n unique tags with most words, desc."""
        seen = {}
        for row in self.rows:
            tag = row.get("tag", "")
            if tag and tag not in seen:
                seen[tag] = len(tag.split())
        return dict(sorted(seen.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n):
        """Return list of top-n unique tags by character length, desc."""
        seen = {}
        for row in self.rows:
            tag = row.get("tag", "")
            if tag and tag not in seen:
                seen[tag] = len(tag)
        top = sorted(seen.items(), key=lambda x: x[1], reverse=True)[:n]
        return [t for t, _ in top]

    def most_words_and_longest(self, n):
        """Return list: intersection of top-n most-words and top-n longest tags."""
        top_words = set(self.most_words(n).keys())
        top_long = set(self.longest(n))
        return list(top_words & top_long)

    def most_popular(self, n):
        """Return {tag -> frequency} for top-n most used tags (duplicates counted), desc."""
        counter = Counter()
        for row in self.rows:
            tag = row.get("tag", "")
            if tag:
                counter[tag] += 1
        return dict(counter.most_common(n))

    def tags_with(self, word):
        """Return sorted list of unique tags that contain `word` (case-insensitive)."""
        word_lower = word.lower()
        found = set()
        for row in self.rows:
            tag = row.get("tag", "")
            if tag and word_lower in tag.lower():
                found.add(tag)
        return sorted(found)


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

class Links:
    """Analyzing data from links.csv with Wikidata enrichment (via IMDb IDs).

    Dataset schema: movieId, imdbId, tmdbId
    Uses Wikidata public SPARQL API — no API key required.
    Uses first 1000 rows.
    """

    def __init__(self, path_to_the_file):
        self.path = os.path.abspath(path_to_the_file)
        self.rows = _load_csv(self.path, limit=1000)

        movies_path = os.path.join(os.path.dirname(self.path), "movies.csv")
        self._movies_map = {}
        if os.path.exists(movies_path):
            self._movies_map = _load_movies_map(movies_path)

        # In-memory cache: {imdb_id_str -> {field -> value}}
        self._cache = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _imdb_url(self, imdb_id_str):
        """Build IMDB URL (kept for compatibility)."""
        return "https://www.imdb.com/title/tt{}/".format(imdb_id_str.zfill(7))

    def _fetch_wikidata(self, imdb_id_str):
        """Fetch movie metadata from Wikidata SPARQL using a raw imdbId string.

        Returns dict with keys: Director, Budget, Gross, Runtime.
        Falls back to empty dict on any error.
        Results are cached in self._cache.
        """
        if imdb_id_str in self._cache:
            return self._cache[imdb_id_str]

        imdb_full = "tt" + imdb_id_str.zfill(7)

        query = """
        SELECT ?directorLabel ?budget ?gross ?duration WHERE {
          ?film wdt:P345 "%s" .
          OPTIONAL { ?film wdt:P57   ?director . }
          OPTIONAL { ?film wdt:P2130 ?budget   . }
          OPTIONAL { ?film wdt:P2142 ?gross    . }
          OPTIONAL { ?film wdt:P2047 ?duration . }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
        } LIMIT 1
        """ % imdb_full

        url = (
            "https://query.wikidata.org/sparql?"
            + urllib.parse.urlencode({"query": query, "format": "json"})
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "MovieLensAnalysis/1.0 (student project)",
                "Accept": "application/sparql-results+json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            bindings = data.get("results", {}).get("bindings", [])
            if not bindings:
                self._cache[imdb_id_str] = {}
                return {}
            row = bindings[0]
            result = {
                "Director": row["directorLabel"]["value"] if "directorLabel" in row else "N/A",
                "Budget":   row["budget"]["value"]        if "budget"        in row else "N/A",
                "Gross":    row["gross"]["value"]         if "gross"         in row else "N/A",
                # Wikidata duration is already in minutes as decimal e.g. "81"
                "Runtime":  row["duration"]["value"]      if "duration"      in row else "N/A",
            }
            self._cache[imdb_id_str] = result
            return result
        except Exception:
            self._cache[imdb_id_str] = {}
            return {}

    def _get_fields(self, imdb_id_str, fields):
        """Return {field -> value} for the requested fields, using Wikidata."""
        data = self._fetch_wikidata(imdb_id_str)
        return {f: data.get(f, "N/A") for f in fields}

    def _parse_money(self, s):
        """Strip non-digit characters; return int or 0.
        Works for both raw Wikidata numbers ('191796233') and formatted ('$191,796,233').
        """
        s = re.sub(r"[^\d]", "", str(s))
        return int(s) if s else 0

    def _parse_runtime_minutes(self, s):
        """Parse runtime to total minutes (int).
        Wikidata returns plain decimal e.g. '81' or '81.0'.
        Also handles 'Xh Ym' format as fallback.
        """
        try:
            return int(float(s))
        except (ValueError, TypeError):
            hours = re.search(r"(\d+)\s*h", str(s))
            mins  = re.search(r"(\d+)\s*m", str(s))
            h = int(hours.group(1)) if hours else 0
            m = int(mins.group(1))  if mins  else 0
            return h * 60 + m if (h or m) else 0

    def _fetch_all_imdb(self, fields):
        """Fetch Wikidata fields for all loaded rows. Returns list of dicts."""
        data = []
        for row in self.rows:
            movie_id = row["movieId"]
            imdb_id  = row.get("imdbId", "")
            entry = {
                "movieId": movie_id,
                "title":   self._movies_map.get(movie_id, movie_id),
            }
            if imdb_id:
                entry.update(self._get_fields(imdb_id, fields))
            else:
                for f in fields:
                    entry[f] = "N/A"
            data.append(entry)
        return data

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_imdb(self, list_of_movies, list_of_fields):
        """Return list of lists [movieId, field1, field2, ...] sorted by movieId desc.

        Fetches data from Wikidata for each given movieId.
        Falls back to 'N/A' when a movie is not found or a field is missing.

        Args:
            list_of_movies: list of movieId values (int or str)
            list_of_fields: list of field name strings, e.g. ['Director', 'Budget']
        """
        mid_to_imdb = {row["movieId"]: row.get("imdbId", "") for row in self.rows}

        results = []
        for mid in sorted(list_of_movies, key=lambda x: int(x), reverse=True):
            mid_str = str(mid)
            imdb_id = mid_to_imdb.get(mid_str, "")
            row_result = [mid_str]
            if imdb_id:
                parsed = self._get_fields(imdb_id, list_of_fields)
                row_result += [parsed.get(f, "N/A") for f in list_of_fields]
            else:
                row_result += ["N/A"] * len(list_of_fields)
            results.append(row_result)
        return results

    def top_directors(self, n):
        """Return {director -> movie_count} for top-n directors, sorted desc."""
        counts = defaultdict(int)
        for row in self.rows:
            imdb_id = row.get("imdbId", "")
            if not imdb_id:
                continue
            data = self._fetch_wikidata(imdb_id)
            director = data.get("Director", "N/A")
            if director and director != "N/A":
                counts[director] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_expensive(self, n):
        """Return {title -> budget_int} for top-n movies by budget, sorted desc."""
        data = self._fetch_all_imdb(["Budget"])
        results = {
            e["title"]: self._parse_money(e["Budget"])
            for e in data
            if self._parse_money(e.get("Budget", "")) > 0
        }
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_profitable(self, n):
        """Return {title -> profit_int} for top-n movies by (gross - budget), sorted desc."""
        data = self._fetch_all_imdb(["Budget", "Gross"])
        results = {}
        for e in data:
            budget = self._parse_money(e.get("Budget", ""))
            gross  = self._parse_money(e.get("Gross",  ""))
            if budget > 0 or gross > 0:
                results[e["title"]] = gross - budget
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n):
        """Return {title -> runtime_minutes} for top-n longest movies, sorted desc."""
        data = self._fetch_all_imdb(["Runtime"])
        results = {
            e["title"]: self._parse_runtime_minutes(e.get("Runtime", ""))
            for e in data
            if self._parse_runtime_minutes(e.get("Runtime", "")) > 0
        }
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])

    def top_cost_per_minute(self, n):
        """Return {title -> cost_per_min} rounded to 2dp, top-n sorted desc."""
        data = self._fetch_all_imdb(["Budget", "Runtime"])
        results = {}
        for e in data:
            budget = self._parse_money(e.get("Budget", ""))
            rt     = self._parse_runtime_minutes(e.get("Runtime", ""))
            if budget > 0 and rt > 0:
                results[e["title"]] = round(budget / rt, 2)
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:n])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class Tests:
    """PyTest test class for all methods of Movies, Ratings, Tags, Links."""

    def _get_data_dir(self):
        base = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(base) == "src":
            return os.path.abspath(os.path.join(base, "..", "datasets", "ml-latest-small"))
        return os.path.abspath(os.path.join(base, "datasets", "ml-latest-small"))

    def _path(self, fname):
        return os.path.join(self._get_data_dir(), fname)

    # ---- Movies ----

    def test_movies_dist_by_release_is_dict(self):
        result = Movies(self._path("movies.csv")).dist_by_release()
        assert isinstance(result, dict)

    def test_movies_dist_by_release_keys_are_int(self):
        result = Movies(self._path("movies.csv")).dist_by_release()
        for key in result:
            assert isinstance(key, int)

    def test_movies_dist_by_release_values_are_int(self):
        result = Movies(self._path("movies.csv")).dist_by_release()
        for val in result.values():
            assert isinstance(val, int)

    def test_movies_dist_by_release_sorted_desc(self):
        result = Movies(self._path("movies.csv")).dist_by_release()
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_movies_dist_by_genres_is_dict(self):
        result = Movies(self._path("movies.csv")).dist_by_genres()
        assert isinstance(result, dict)

    def test_movies_dist_by_genres_keys_are_str(self):
        result = Movies(self._path("movies.csv")).dist_by_genres()
        for key in result:
            assert isinstance(key, str)

    def test_movies_dist_by_genres_sorted_desc(self):
        result = Movies(self._path("movies.csv")).dist_by_genres()
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_movies_most_genres_is_dict(self):
        result = Movies(self._path("movies.csv")).most_genres(5)
        assert isinstance(result, dict)

    def test_movies_most_genres_sorted_desc(self):
        result = Movies(self._path("movies.csv")).most_genres(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_movies_most_genres_len(self):
        n = 7
        result = Movies(self._path("movies.csv")).most_genres(n)
        assert len(result) <= n

    # ---- Ratings.Movies ----

    def test_ratings_movies_dist_by_year_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.dist_by_year()
        assert isinstance(result, dict)

    def test_ratings_movies_dist_by_year_keys_are_int(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.dist_by_year()
        for k in result:
            assert isinstance(k, int)

    def test_ratings_movies_dist_by_year_sorted_asc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.dist_by_year()
        keys = list(result.keys())
        assert keys == sorted(keys)

    def test_ratings_movies_dist_by_rating_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.dist_by_rating()
        assert isinstance(result, dict)

    def test_ratings_movies_dist_by_rating_keys_are_float(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.dist_by_rating()
        for k in result:
            assert isinstance(k, float)

    def test_ratings_movies_dist_by_rating_sorted_asc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.dist_by_rating()
        keys = list(result.keys())
        assert keys == sorted(keys)

    def test_ratings_movies_top_by_num_of_ratings_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.movies.top_by_num_of_ratings(5), dict)

    def test_ratings_movies_top_by_num_of_ratings_sorted_desc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.top_by_num_of_ratings(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_ratings_movies_top_by_ratings_average_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.movies.top_by_ratings(5, "average"), dict)

    def test_ratings_movies_top_by_ratings_median_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.movies.top_by_ratings(5, "median"), dict)

    def test_ratings_movies_top_by_ratings_sorted_desc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.top_by_ratings(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_ratings_movies_top_controversial_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.movies.top_controversial(5), dict)

    def test_ratings_movies_top_controversial_sorted_desc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.movies.top_controversial(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    # ---- Ratings.Users ----

    def test_ratings_users_dist_by_ratings_number_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.users.dist_by_ratings_number(), dict)

    def test_ratings_users_dist_by_ratings_number_sorted_asc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.users.dist_by_ratings_number()
        keys = list(result.keys())
        assert keys == sorted(keys)

    def test_ratings_users_dist_by_ratings_metric_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.users.dist_by_ratings_metric(), dict)

    def test_ratings_users_dist_by_ratings_metric_sorted_asc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.users.dist_by_ratings_metric()
        keys = list(result.keys())
        assert keys == sorted(keys)

    def test_ratings_users_top_controversial_is_dict(self):
        r = Ratings(self._path("ratings.csv"))
        assert isinstance(r.users.top_controversial(5), dict)

    def test_ratings_users_top_controversial_sorted_desc(self):
        r = Ratings(self._path("ratings.csv"))
        result = r.users.top_controversial(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    # ---- Tags ----

    def test_tags_most_words_is_dict(self):
        t = Tags(self._path("tags.csv"))
        assert isinstance(t.most_words(5), dict)

    def test_tags_most_words_sorted_desc(self):
        t = Tags(self._path("tags.csv"))
        result = t.most_words(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_tags_longest_is_list(self):
        t = Tags(self._path("tags.csv"))
        assert isinstance(t.longest(5), list)

    def test_tags_longest_elements_are_str(self):
        t = Tags(self._path("tags.csv"))
        for item in t.longest(5):
            assert isinstance(item, str)

    def test_tags_most_words_and_longest_is_list(self):
        t = Tags(self._path("tags.csv"))
        assert isinstance(t.most_words_and_longest(5), list)

    def test_tags_most_popular_is_dict(self):
        t = Tags(self._path("tags.csv"))
        assert isinstance(t.most_popular(5), dict)

    def test_tags_most_popular_sorted_desc(self):
        t = Tags(self._path("tags.csv"))
        result = t.most_popular(10)
        vals = list(result.values())
        assert vals == sorted(vals, reverse=True)

    def test_tags_tags_with_is_list(self):
        t = Tags(self._path("tags.csv"))
        assert isinstance(t.tags_with("sci"), list)

    def test_tags_tags_with_sorted_alpha(self):
        t = Tags(self._path("tags.csv"))
        result = t.tags_with("sci")
        assert result == sorted(result)

    # ---- Links ----

    def test_links_get_imdb_is_list(self):
        l = Links(self._path("links.csv"))
        result = l.get_imdb(["1", "2"], ["Director"])
        assert isinstance(result, list)

    def test_links_get_imdb_elements_are_lists(self):
        l = Links(self._path("links.csv"))
        result = l.get_imdb(["1", "2"], ["Director"])
        for item in result:
            assert isinstance(item, list)

    def test_links_get_imdb_sorted_desc(self):
        l = Links(self._path("links.csv"))
        result = l.get_imdb(["1", "2", "3"], ["Director"])
        ids = [int(row[0]) for row in result]
        assert ids == sorted(ids, reverse=True)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pytest as _pytest
    _pytest.main([__file__, "-v"])