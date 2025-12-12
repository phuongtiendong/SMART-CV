"""OCR functions for extracting text from PDF files."""
import base64
import logging
from io import BytesIO
from typing import List

import fitz  # PyMuPDF
import requests
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def encode_image_to_base64(image: Image.Image, max_dim: int = 2000, quality: int = 95) -> str:
    """Resize image and encode to base64 for OCR."""
    img = image.copy()
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def ocr_image_base64(img_b64: str, api_key: str) -> str:
    """OCR a base64-encoded image using Google Vision API."""
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    payload = {
        "requests": [
            {"image": {"content": img_b64}, "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]}
        ]
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["responses"][0].get("fullTextAnnotation", {}).get("text", "") or ""


def ocr_pdf(file_bytes: bytes, api_key: str) -> str:
    """OCR PDF to text using Google Vision API."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        logger.error("Could not open PDF for OCR: %s", exc)
        return ""

    markdown_parts: List[str] = []
    for idx in range(len(doc)):
        page = doc.load_page(idx)
        pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
        image = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
        image = ImageOps.exif_transpose(image)

        img_b64 = encode_image_to_base64(image)
        try:
            text = ocr_image_base64(img_b64, api_key)
            markdown_parts.append(text)
        except Exception as exc:
            logger.warning("OCR error for page %s: %s", idx, exc)
    return "\n".join(markdown_parts)
