import re
from typing import Optional

import httpx

from app.core.config import settings


class SerpApiLookupError(Exception):
    pass


INGREDIENT_MARKER = re.compile(
    r"\b(?:ingredients?|contains)\s*[:\-]\s*(?P<ingredients>[^.]{20,700})",
    re.I,
)
SPACE_PATTERN = re.compile(r"\s+")


def _clean_text(value: str) -> str:
    return SPACE_PATTERN.sub(" ", value or "").strip()


def _product_query(barcode: str, product: Optional[dict] = None) -> str:
    product = product or {}
    parts = [
        product.get("brands") or product.get("brand"),
        product.get("product_name"),
        barcode,
        "ingredients",
    ]
    return " ".join(str(part).strip() for part in parts if part)


def _collect_result_text(data: dict) -> list[str]:
    texts: list[str] = []
    for result in data.get("organic_results") or []:
        for key in ("title", "snippet", "source"):
            value = result.get(key)
            if value:
                texts.append(_clean_text(str(value)))
        for word in result.get("snippet_highlighted_words") or []:
            texts.append(_clean_text(str(word)))
        rich_snippet = result.get("rich_snippet")
        if isinstance(rich_snippet, dict):
            texts.append(_clean_text(str(rich_snippet)))

    answer_box = data.get("answer_box")
    if isinstance(answer_box, dict):
        for key in ("title", "snippet", "answer"):
            value = answer_box.get(key)
            if value:
                texts.append(_clean_text(str(value)))

    return [text for text in texts if text]


def _extract_ingredients(texts: list[str]) -> str:
    marked: list[str] = []
    for text in texts:
        for match in INGREDIENT_MARKER.finditer(text):
            marked.append(_clean_text(match.group("ingredients")))
    if marked:
        return "; ".join(dict.fromkeys(marked))

    ingredient_like = [
        text
        for text in texts
        if any(word in text.lower() for word in ["ingredient", "contains", "allergen"])
    ]
    return "\n".join(dict.fromkeys(ingredient_like[:8]))


def _best_product_name(data: dict, product: Optional[dict] = None, barcode: str = "") -> str:
    product = product or {}
    existing = product.get("product_name")
    if existing:
        return existing
    for result in data.get("organic_results") or []:
        title = _clean_text(str(result.get("title") or ""))
        if title:
            return title[:180]
    return f"Product {barcode}"


async def find_product_ingredients(barcode: str, product: Optional[dict] = None) -> dict:
    if not settings.serpapi_api_key:
        raise SerpApiLookupError("SerpAPI key is not configured")

    params = {
        "engine": "google",
        "q": _product_query(barcode, product),
        "api_key": settings.serpapi_api_key,
        "num": 8,
        "hl": "en",
    }
    timeout = httpx.Timeout(settings.serpapi_timeout_seconds, connect=10)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(settings.serpapi_base_url, params=params)
            response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        raise SerpApiLookupError(f"SerpAPI lookup failed: {exc.__class__.__name__}") from exc
    except ValueError as exc:
        raise SerpApiLookupError("SerpAPI returned invalid JSON") from exc

    texts = _collect_result_text(data)
    ingredients_text = _extract_ingredients(texts)
    if not ingredients_text:
        raise SerpApiLookupError("No ingredient-like search results found")

    return {
        "barcode": barcode,
        "product_name": _best_product_name(data, product, barcode),
        "ingredients_text": ingredients_text,
        "ingredients_source": "serpapi_google_search",
        "serpapi_query": params["q"],
        "serpapi_context": "\n".join(dict.fromkeys(texts[:10])),
    }
