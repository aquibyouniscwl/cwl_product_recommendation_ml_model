from typing import Dict, Any

class SimpleMemoryCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def exists(self, key: str) -> bool:
        return key in self._cache

    def clear(self) -> None:
        self._cache.clear()

global_cache = SimpleMemoryCache()
