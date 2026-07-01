from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.config import MIMO_API_KEY, MIMO_BASE_URL, MIMO_MODEL, MIMO_PDF_MAX_PAGES
from app.models.schema import FieldSchema


SYSTEM_PROMPT = """You are an enterprise API specification parser for EDI integrations.
Extract target request payload fields from PDF interface documents.
Return strict JSON only. Do not include markdown.
Prefer the main request message section over response, webhook, attachment, master-data, revision history, or sample response sections.
Preserve exact API tag names and nested JSON paths. Include array paths with [] when visible.
Do not invent source database mappings."""


def _safe_json_loads(content: str) -> dict[str, Any]:
    try:
        return json.loads(content or "{}")
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content or "", flags=re.S)
        if match:
            return json.loads(match.group(0))
    raise ValueError("MIMO did not return valid JSON.")


def _page_texts(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    return [page.extract_text() or "" for page in reader.pages]


def _select_request_pages(page_texts: list[str], max_pages: int) -> list[int]:
    """Find the main filing request-message pages and avoid response/sample sections."""
    start: int | None = None
    end = len(page_texts)
    for index, text in enumerate(page_texts):
        normalized = re.sub(r"\s+", " ", text.lower())
        if "2.4 request message" in normalized or ("request message" in normalized and "api tag" in normalized):
            start = index
            break
    if start is None:
        return list(range(min(len(page_texts), max_pages)))

    for index in range(start + 1, len(page_texts)):
        normalized = re.sub(r"\s+", " ", page_texts[index].lower())
        if any(marker in normalized for marker in ("2.5 sample message", "response message", "web hook", "attachment api")):
            end = index
            break
    pages = list(range(start, min(end, start + max_pages)))
    return pages or [start]


def _render_pdf_pages(path: Path, page_indexes: list[int]) -> list[str]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for MIMO multimodal PDF parsing. Run `pip install -r requirements.txt`.") from exc

    document = fitz.open(str(path))
    images: list[str] = []
    try:
        for index in page_indexes:
            page = document.load_page(index)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
            images.append(base64.b64encode(pixmap.tobytes("jpeg")).decode("ascii"))
    finally:
        document.close()
    return images


def _call_mimo(messages: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is not installed. Run `pip install -r requirements.txt`.") from exc

    if not MIMO_API_KEY:
        raise RuntimeError("MIMO_API_KEY is not configured.")
    if not MIMO_BASE_URL:
        raise RuntimeError("MIMO_BASE_URL is not configured.")

    client = OpenAI(api_key=MIMO_API_KEY, base_url=MIMO_BASE_URL)
    completion = client.chat.completions.create(
        model=MIMO_MODEL,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    return _safe_json_loads(completion.choices[0].message.content or "{}")


def _build_user_content(source_name: str, selected_text: str, images: list[str]) -> list[dict[str, Any]]:
    prompt = {
        "source_document": source_name,
        "task": "Extract the main API filing request payload fields from these PDF pages.",
        "selection_hint": "For MPCI documents, prefer section 2.4 Request Message. Ignore sample response, webhook response, attachment API, and vessel master sections unless they are the only request section.",
        "output_schema": {
            "endpoint": "string, optional. Use '/' if not stated.",
            "method": "HTTP method, usually POST.",
            "fields": [
                {
                    "param_path": "API tag or nested JSON path. Use [] for array items when applicable.",
                    "param_name": "short API tag name",
                    "description": "business meaning, validation, possible values, and M/O/C note if visible",
                    "type": "data type or original validation format",
                    "required": "boolean, true when M/O/C is M or clearly mandatory",
                    "example": "optional sample value",
                }
            ],
        },
        "extracted_pdf_text": selected_text[:30000],
    }
    content: list[dict[str, Any]] = [{"type": "text", "text": json.dumps(prompt, ensure_ascii=False)}]
    for image in images:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}})
    return content


def parse_api_pdf_with_mimo(path: str | Path) -> tuple[str, str, list[FieldSchema]]:
    """Parse a PDF API document with MIMO multimodal vision before text fallbacks."""
    source = Path(path)
    texts = _page_texts(source)
    page_indexes = _select_request_pages(texts, MIMO_PDF_MAX_PAGES)
    selected_text = "\n\n".join(f"# Page {index + 1}\n{texts[index]}" for index in page_indexes)
    images = _render_pdf_pages(source, page_indexes)
    response = _call_mimo(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_content(source.name, selected_text, images)},
        ]
    )

    fields: list[FieldSchema] = []
    seen: set[str] = set()
    for item in response.get("fields") or []:
        if not isinstance(item, dict):
            continue
        field_name = str(item.get("param_path") or item.get("param_name") or "").strip()
        if not field_name or field_name in seen:
            continue
        seen.add(field_name)
        fields.append(
            FieldSchema(
                field_name=field_name,
                description=str(item.get("description") or "").strip(),
                type=str(item.get("type") or "string").strip().lower(),
                required=_parse_required(item.get("required")),
                example=item.get("example"),
            )
        )
    if not fields:
        raise ValueError("MIMO could not extract API fields from the PDF.")
    return str(response.get("endpoint") or "/"), str(response.get("method") or "POST").upper(), fields


def _parse_required(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "m", "mandatory", "required", "是", "必填"}
