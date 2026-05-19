import httpx
from app.core.config import settings


class ProductNotFoundError(Exception):
    pass


class ProductLookupError(Exception):
    pass


IMPORTANT_NUTRIMENT_KEYS = {
    "energy-kcal_100g",
    "energy_100g",
    "fat_100g",
    "saturated-fat_100g",
    "carbohydrates_100g",
    "sugars_100g",
    "fiber_100g",
    "proteins_100g",
    "salt_100g",
    "sodium_100g",
    "nutrition-score-fr_100g",
    "nova-group_100g",
}
PRODUCT_FIELDS = [
    "code",
    "status",
    "status_verbose",
    "product_name",
    "generic_name",
    "brands",
    "ingredients_text",
    "ingredients",
    "nutriments",
    "image_front_url",
    "image_url",
    "categories",
    "allergens_tags",
    "additives_tags",
    "labels_tags",
    "countries_tags",
    "nutrition_grades",
    "nutriscore_data",
    "nova_group",
]
REQUEST_HEADERS = {
    "Accept": "application/json",
}


def extract_nutrition(nutriments: dict) -> dict:
    return {key: value for key, value in (nutriments or {}).items() if key in IMPORTANT_NUTRIMENT_KEYS}


def structure_product(raw: dict, barcode: str) -> dict:
    if not raw or raw.get("status") == 0 or not raw.get("product"):
        raise ProductNotFoundError(f"No Open Food Facts product found for barcode {barcode}")
    product = raw.get("product", {}) if raw else {}
    categories = [item.strip() for item in (product.get("categories") or "").split(",") if item.strip()]
    nutriments = extract_nutrition(product.get("nutriments") or {})
    return {
        "barcode": barcode,
        "product_name": product.get("product_name") or product.get("generic_name") or f"Product {barcode}",
        "ingredients_text": product.get("ingredients_text") or "",
        "ingredients": product.get("ingredients") or [],
        "allergens_tags": product.get("allergens_tags") or [],
        "additives_tags": product.get("additives_tags") or [],
        "nutriments": nutriments,
        "nutrition": nutriments,
        "image_front_url": product.get("image_front_url") or product.get("image_url"),
        "product_image_url": product.get("image_front_url") or product.get("image_url"),
        "brands": product.get("brands") or "",
        "brand": product.get("brands") or "",
        "categories": categories,
        "labels_tags": product.get("labels_tags") or [],
        "countries_tags": product.get("countries_tags") or [],
        "nutrition_grades": product.get("nutrition_grades") or "",
        "nutriscore_data": product.get("nutriscore_data") or {},
        "nova_group": product.get("nova_group"),
        "source": "openfoodfacts"
    }


async def fetch_product(barcode: str) -> dict:
    base_url = settings.openfoodfacts_base_url.rstrip("/")
    headers = {**REQUEST_HEADERS, "User-Agent": settings.openfoodfacts_user_agent}
    requests = [
        (f"{base_url}/api/v2/product/{barcode}.json", {"fields": ",".join(PRODUCT_FIELDS)}),
        (f"{base_url}/api/v0/product/{barcode}.json", None),
    ]
    last_error = None
    for url, params in requests:
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
            return structure_product(response.json(), barcode)
        except ProductNotFoundError as exc:
            last_error = exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                last_error = ProductNotFoundError(f"No Open Food Facts product found for barcode {barcode}")
                continue
            last_error = exc
        except httpx.HTTPError as exc:
            last_error = exc
    if isinstance(last_error, ProductNotFoundError):
        raise last_error
    raise ProductLookupError(f"Open Food Facts lookup failed: {last_error.__class__.__name__ if last_error else 'unknown error'}")
