import os
import csv
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
from src.utils.logger import logger

# =====================================================
# CONFIG
# =====================================================
# FIX #1: Changed from 3 levels (..) to 2 levels (..)
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

REQUEST_PATTERNS_CSV = os.path.join(
    BASE_DIR,
    "benchmark",
    "analytics",
    "request_patterns.csv",
)

RECOMMENDATION_PATTERNS_CSV = os.path.join(
    BASE_DIR,
    "benchmark",
    "analytics",
    "recommendation_patterns.csv",
)


# =====================================================
# PATTERN ANALYTICS
# =====================================================
class PatternAnalytics:
    def __init__(self):
        self._lock = threading.Lock()
        # request_pattern -> {"count": int, "first_seen": str, "last_seen": str}
        self.request_patterns: Dict[str, Dict[str, Any]] = {}
        # (request_pattern, recommendation_pattern) -> {"count": int, "last_seen": str}
        self.recommendation_patterns: Dict[tuple, Dict[str, Any]] = {}
        self.request_counter = 0
        self.save_every_n_requests = 50

    def auto_save(self):
        should_save = False
        with self._lock:
            self.request_counter += 1
            if self.request_counter >= self.save_every_n_requests:
                self.request_counter = 0
                should_save = True
        if should_save:
            try:
                self.save_pattern_analytics()
            except Exception as e:
                logger.error(
                    f"Auto save failed: {e}"
                )
    def force_save(self):
        try:
            self.save_pattern_analytics()
        except Exception as e:

            logger.error(
                f"Force save failed: {e}"
            )

    # =================================================
    # GENERATE PATTERN KEY
    # =================================================
    def generate_pattern_key(
        self,
        cart_products: List[str],
        enrolled_products: Optional[List[str]] = None,
    ) -> str:
        if enrolled_products is None:
            enrolled_products = []
        cart_key = "|".join(sorted(cart_products))
        enrolled_key = "|".join(sorted(enrolled_products))
        return f"cart:{cart_key}::enrolled:{enrolled_key}"

    # =================================================
    # GENERATE RECOMMENDATION PATTERN
    # =================================================
    def generate_recommendation_pattern(
        self, recommendation_ids: List[str]
    ) -> str:
        return "|".join(sorted(recommendation_ids))

    # =================================================
    # TRACK REQUEST PATTERN
    # =================================================
    def track_request_pattern(
        self,
        cart_products: List[str],
        enrolled_products: Optional[List[str]] = None,
    ) -> str:
        pattern_key = self.generate_pattern_key(cart_products, enrolled_products)
        now = datetime.utcnow().isoformat()
        with self._lock:
            if pattern_key in self.request_patterns:
                self.request_patterns[pattern_key]["count"] += 1
                self.request_patterns[pattern_key]["last_seen"] = now
            else:
                self.request_patterns[pattern_key] = {
                    "count": 1,
                    "first_seen": now,
                    "last_seen": now,
                }
        return pattern_key

    # =================================================
    # TRACK RECOMMENDATION PATTERN
    # =================================================
    def track_recommendation_pattern(
        self,
        cart_products: List[str],
        enrolled_products: Optional[List[str]] = None,
        recommendation_ids: Optional[List[str]] = None,
    ) -> None:
        if recommendation_ids is None:
            recommendation_ids = []
        request_key = self.generate_pattern_key(cart_products, enrolled_products)
        rec_key = self.generate_recommendation_pattern(recommendation_ids)
        now = datetime.utcnow().isoformat()
        with self._lock:
            composite_key = (request_key, rec_key)
            if composite_key in self.recommendation_patterns:
                self.recommendation_patterns[composite_key]["count"] += 1
                self.recommendation_patterns[composite_key]["last_seen"] = now
            else:
                self.recommendation_patterns[composite_key] = {
                    "count": 1,
                    "last_seen": now,
                }

    # =================================================
    # LOAD PATTERN ANALYTICS
    # =================================================
    # FIX #2: Added robust error handling for CSV loading
    def load_pattern_analytics(self) -> None:
        with self._lock:
            # Load request patterns
            if os.path.exists(REQUEST_PATTERNS_CSV):
                try:
                    with open(REQUEST_PATTERNS_CSV, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                # Skip rows with missing critical values
                                if not row.get("request_count") or row.get("request_count") is None:
                                    logger.warning(f"Skipping request pattern row with missing count: {row}")
                                    continue
                                if not row.get("request_pattern") or row.get("request_pattern") is None:
                                    logger.warning(f"Skipping request pattern row with missing pattern: {row}")
                                    continue

                                pattern = row["request_pattern"]
                                count = int(row["request_count"])
                                first_seen = row.get("first_seen", "")
                                last_seen = row.get("last_seen", "")

                                if pattern in self.request_patterns:
                                    self.request_patterns[pattern]["count"] += count
                                    if first_seen and first_seen < self.request_patterns[pattern]["first_seen"]:
                                        self.request_patterns[pattern]["first_seen"] = first_seen
                                    if last_seen and last_seen > self.request_patterns[pattern]["last_seen"]:
                                        self.request_patterns[pattern]["last_seen"] = last_seen
                                else:
                                    self.request_patterns[pattern] = {
                                        "count": count,
                                        "first_seen": first_seen,
                                        "last_seen": last_seen,
                                    }
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Error parsing request pattern row: {row}. Error: {e}")
                                continue
                except Exception as e:
                    logger.error(f"Failed to load request patterns CSV: {e}")

            # Load recommendation patterns
            if os.path.exists(RECOMMENDATION_PATTERNS_CSV):
                try:
                    with open(RECOMMENDATION_PATTERNS_CSV, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                # Skip rows with missing critical values
                                if not row.get("recommendation_count") or row.get("recommendation_count") is None:
                                    logger.warning(f"Skipping recommendation pattern row with missing count: {row}")
                                    continue
                                if not row.get("request_pattern") or row.get("request_pattern") is None:
                                    logger.warning(f"Skipping recommendation pattern row with missing request_pattern: {row}")
                                    continue

                                req_pattern = row["request_pattern"]
                                rec_pattern = row["recommendation_pattern"]
                                count = int(row["recommendation_count"])
                                last_seen = row.get("last_seen", "")

                                composite_key = (req_pattern, rec_pattern)
                                if composite_key in self.recommendation_patterns:
                                    self.recommendation_patterns[composite_key]["count"] += count
                                    if last_seen and last_seen > self.recommendation_patterns[composite_key]["last_seen"]:
                                        self.recommendation_patterns[composite_key]["last_seen"] = last_seen
                                else:
                                    self.recommendation_patterns[composite_key] = {
                                        "count": count,
                                        "last_seen": last_seen,
                                    }
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Error parsing recommendation pattern row: {row}. Error: {e}")
                                continue
                except Exception as e:
                    logger.error(f"Failed to load recommendation patterns CSV: {e}")

        logger.info("Pattern Analytics Loaded")

    # =================================================
    # SAVE PATTERN ANALYTICS
    # =================================================
    def save_pattern_analytics(self) -> None:
        os.makedirs(
            os.path.dirname(
                REQUEST_PATTERNS_CSV
            ),
            exist_ok=True,
        )
        with self._lock:
            # Merge with existing request patterns CSV
            merged_requests: Dict[str, Dict[str, Any]] = {}
            if os.path.exists(REQUEST_PATTERNS_CSV):
                try:
                    with open(REQUEST_PATTERNS_CSV, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                if not row.get("request_count") or row.get("request_count") is None:
                                    continue
                                pattern = row["request_pattern"]
                                merged_requests[pattern] = {
                                    "count": int(row["request_count"]),
                                    "first_seen": row.get("first_seen", ""),
                                    "last_seen": row.get("last_seen", ""),
                                }
                            except (ValueError, TypeError):
                                continue
                except Exception as e:
                    logger.warning(f"Could not read existing request patterns: {e}")

            # Merge in-memory data
            for pattern, data in self.request_patterns.items():
                if pattern in merged_requests:
                    merged_requests[pattern]["count"] += data["count"]
                    if data["first_seen"] < merged_requests[pattern]["first_seen"]:
                        merged_requests[pattern]["first_seen"] = data["first_seen"]
                    if data["last_seen"] > merged_requests[pattern]["last_seen"]:
                        merged_requests[pattern]["last_seen"] = data["last_seen"]
                else:
                    merged_requests[pattern] = data.copy()

            # Write request patterns
            os.makedirs(os.path.dirname(REQUEST_PATTERNS_CSV), exist_ok=True)
            with open(REQUEST_PATTERNS_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["request_pattern", "request_count", "first_seen", "last_seen"])
                for pattern, data in merged_requests.items():
                    writer.writerow([pattern, data["count"], data["first_seen"], data["last_seen"]])

            # Merge with existing recommendation patterns CSV
            merged_recs: Dict[tuple, Dict[str, Any]] = {}
            if os.path.exists(RECOMMENDATION_PATTERNS_CSV):
                try:
                    with open(RECOMMENDATION_PATTERNS_CSV, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                if not row.get("recommendation_count") or row.get("recommendation_count") is None:
                                    continue
                                key = (row["request_pattern"], row["recommendation_pattern"])
                                merged_recs[key] = {
                                    "count": int(row["recommendation_count"]),
                                    "last_seen": row.get("last_seen", ""),
                                }
                            except (ValueError, TypeError):
                                continue
                except Exception as e:
                    logger.warning(f"Could not read existing recommendation patterns: {e}")

            # Merge in-memory data
            for key, data in self.recommendation_patterns.items():
                if key in merged_recs:
                    merged_recs[key]["count"] += data["count"]
                    if data["last_seen"] > merged_recs[key]["last_seen"]:
                        merged_recs[key]["last_seen"] = data["last_seen"]
                else:
                    merged_recs[key] = data.copy()

            # Write recommendation patterns
            with open(RECOMMENDATION_PATTERNS_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["request_pattern", "recommendation_pattern", "recommendation_count", "last_seen"])
                for (req_pat, rec_pat), data in merged_recs.items():
                    writer.writerow([req_pat, rec_pat, data["count"], data["last_seen"]])

            # Clear in-memory after saving to prevent double-counting
            self.request_patterns.clear()
            self.recommendation_patterns.clear()
            logger.info(
                f"Pattern Analytics Saved | "
                f"Requests={len(merged_requests)} | "
                f"Recommendations={len(merged_recs)}"
            )

    # =================================================
    # GET TOP PATTERNS
    # =================================================
    def get_top_patterns(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            # Combine in-memory + CSV data
            combined: Dict[str, int] = {}
            # In-memory data
            for pattern, data in self.request_patterns.items():
                combined[pattern] = combined.get(pattern, 0) + data["count"]
            # CSV data
            if os.path.exists(REQUEST_PATTERNS_CSV):
                try:
                    with open(REQUEST_PATTERNS_CSV, "r", newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                if not row.get("request_count") or row.get("request_count") is None:
                                    continue
                                pattern = row["request_pattern"]
                                combined[pattern] = combined.get(pattern, 0) + int(row["request_count"])
                            except (ValueError, TypeError):
                                continue
                except Exception:
                    pass
        sorted_patterns = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return [{"pattern": p, "count": c} for p, c in sorted_patterns[:limit]]


# =====================================================
# SINGLETON INSTANCE
# =====================================================
pattern_analytics = PatternAnalytics()