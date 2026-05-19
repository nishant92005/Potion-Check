from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

try:
    import pytesseract
except ImportError:
    pytesseract = None


def extract_ingredients_from_text(text: str) -> str:
    normalized = " ".join(text.replace("\n", " ").split())
    lowered = normalized.lower()
    for keyword in ["ingredients:", "ingredient:", "contains:"]:
        idx = lowered.find(keyword)
        if idx >= 0:
            return normalized[idx + len(keyword):].strip(" .;")
    return normalized


def run_ocr(path: Path) -> str:
    if pytesseract is None:
        return ""
    image = Image.open(path)
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.8)
    text = pytesseract.image_to_string(image)
    return extract_ingredients_from_text(text)
