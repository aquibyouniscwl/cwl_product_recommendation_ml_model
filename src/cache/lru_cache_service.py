import threading
from collections import OrderedDict
from typing import Optional, Dict, Any
from src.utils.logger import logger

# =====================================================
# CONFIG
# =====================================================
LRU_MAX_SIZE = 1000
LRU_ENABLED = True


# =====================================================
# LRU CACHE SERVICE
# =====================================================
class LRUCacheService:
    def __init__(self, maxsize: int = LRU_MAX_SIZE):
        self._lock = threading.Lock()
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._maxsize = maxsize
        self._hits = 0
        self._misses = 0

    # =================================================
    # GET FROM LRU
    # =================================================
    def get_from_lru(self, cache_key: str) -> Optional[Dict[str, Any]]:
        if not LRU_ENABLED:
            return None
        with self._lock:
            if cache_key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(cache_key)
                self._hits += 1
                return self._cache[cache_key]
            self._misses += 1
            return None

    # =================================================
    # STORE IN LRU
    # =================================================
    def store_in_lru(self, cache_key: str, value: Dict[str, Any]) -> None:
        if not LRU_ENABLED:
            return
        with self._lock:
            if cache_key in self._cache:
                # Update existing and move to end
                self._cache.move_to_end(cache_key)
                self._cache[cache_key] = value
            else:
                self._cache[cache_key] = value
                # Evict oldest if over capacity
                if len(self._cache) > self._maxsize:
                    self._cache.popitem(last=False)

    # =================================================
    # CLEAR LRU CACHE
    # =================================================
    def clear_lru_cache(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
        logger.info("LRU cache cleared.")

    # =================================================
    # GET LRU STATS
    # =================================================
    def get_lru_stats(self) -> Dict[str, int]:
        with self._lock:
            return {
                "lru_hits": self._hits,
                "lru_misses": self._misses,
                "lru_size": len(self._cache),
            }


# =====================================================
# SINGLETON INSTANCE
# =====================================================
lru_cache_service = LRUCacheService()
