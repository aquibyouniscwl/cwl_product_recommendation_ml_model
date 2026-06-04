import hashlib
import json


def generate_cache_key(cart_products, enrolled_products, top_k):
    payload = {
        "cart_products": sorted(cart_products),
        "enrolled_products": sorted(enrolled_products),
        "top_k": top_k,
    }
    payload_string = json.dumps(payload, sort_keys=True)
    hashed = hashlib.md5(payload_string.encode()).hexdigest()
    return f"recommend:{hashed}"
