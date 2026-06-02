from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
import json
import logging
import re
from typing import Any
from urllib import error, request

from config import CLIENT_CODE_PREFIX, OPENAI_API_KEY, OPENAI_VISION_MODEL


logger = logging.getLogger(__name__)


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
MAX_IMAGE_BYTES = 20 * 1024 * 1024
SUPPORTED_IMAGE_MIME_TYPES = {
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/webp",
}


class ParcelLabelAIError(Exception):
    pass


@dataclass(frozen=True)
class ParcelLabelExtraction:
    client_code: str | None
    track_code: str | None
    confidence: float
    notes: str


def _clean_client_code(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = re.sub(r"[^A-Z0-9]", "", value.upper())
    return cleaned or None


def _clean_track_code(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    return cleaned or None


def _parse_extraction(value: Any) -> ParcelLabelExtraction:
    if not isinstance(value, dict):
        raise ParcelLabelAIError("AI ҷавоби нодуруст баргардонд.")

    confidence = value.get("confidence", 0)
    if not isinstance(confidence, (int, float)):
        confidence = 0

    notes = value.get("notes", "")
    if not isinstance(notes, str):
        notes = ""

    return ParcelLabelExtraction(
        client_code=_clean_client_code(value.get("client_code")),
        track_code=_clean_track_code(value.get("track_code")),
        confidence=max(0.0, min(float(confidence), 1.0)),
        notes=notes.strip(),
    )


def _response_output_text(payload: Any) -> str:
    if not isinstance(payload, dict):
        raise ParcelLabelAIError("AI ҷавоби нодуруст баргардонд.")

    for item in payload.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue

        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return text

    raise ParcelLabelAIError("AI аз расм маълумот бароварда натавонист.")


def _request_payload(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    encoded_image = base64.b64encode(image_bytes).decode("ascii")
    prefix = CLIENT_CODE_PREFIX.strip().upper() or "AK"
    return {
        "model": OPENAI_VISION_MODEL,
        "store": False,
        "reasoning": {"effort": "low"},
        "max_output_tokens": 800,
        "instructions": (
            "You extract cargo parcel label data. Never guess. "
            "Return null when a value is not clearly readable. "
            "A photo contains exactly one parcel. "
            "The client_code is the warehouse recipient/client code, commonly "
            f"starting with {prefix} and usually written at the end of the address. "
            "Do not confuse it with a phone number, order number, or address number. "
            "The track_code is the Chinese carrier waybill or shipping tracking number. "
            "Do not confuse it with the marketplace order ID, phone number, barcode "
            "serial, or the internal client code. Read the printed value near the "
            "shipping barcode when possible."
        ),
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract the internal client code and carrier track code "
                            "from this Pinduoduo, Taobao, or Chinese delivery label."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{encoded_image}",
                        "detail": "high",
                    },
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "parcel_label_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "client_code": {
                            "type": ["string", "null"],
                            "description": (
                                "Internal warehouse client code from the address tail."
                            ),
                        },
                        "track_code": {
                            "type": ["string", "null"],
                            "description": "Chinese carrier shipping tracking code.",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": (
                                "Confidence that both extracted values are correct."
                            ),
                        },
                        "notes": {
                            "type": "string",
                            "description": "Short warning when a value is unclear.",
                        },
                    },
                    "required": [
                        "client_code",
                        "track_code",
                        "confidence",
                        "notes",
                    ],
                    "additionalProperties": False,
                },
            },
        },
    }


async def extract_parcel_label(
    image_bytes: bytes,
    mime_type: str,
) -> ParcelLabelExtraction:
    if not OPENAI_API_KEY:
        raise ParcelLabelAIError("OPENAI_API_KEY сабт нашудааст.")

    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise ParcelLabelAIError("Формати расм дастгирӣ намешавад.")

    if not image_bytes:
        raise ParcelLabelAIError("Расм холӣ аст.")

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ParcelLabelAIError("Ҳаҷми расм аз 20 MB зиёд аст.")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = _request_payload(image_bytes, mime_type)

    try:
        response_payload = await asyncio.to_thread(
            _post_openai_response,
            payload,
            headers,
        )
    except ParcelLabelAIError:
        raise
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        logger.exception("OpenAI parcel label extraction request failed")
        raise ParcelLabelAIError(
            "AI хизматрасонӣ ҳоло дастнорас аст. Аз нав кӯшиш кунед.",
        )

    try:
        return _parse_extraction(json.loads(_response_output_text(response_payload)))
    except json.JSONDecodeError as error:
        raise ParcelLabelAIError("AI ҷавоби нодуруст баргардонд.") from error


def _post_openai_response(
    payload: dict[str, Any],
    headers: dict[str, str],
) -> Any:
    openai_request = request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(openai_request, timeout=60) as response:
            return json.load(response)
    except error.HTTPError as http_error:
        logger.warning(
            "OpenAI parcel label extraction failed with status %s",
            http_error.code,
        )
        raise ParcelLabelAIError(
            "AI хизматрасонӣ ҳоло ҷавоб надод. Аз нав кӯшиш кунед.",
        ) from http_error
