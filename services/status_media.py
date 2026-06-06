from services.settings import get_many_settings

from utils.constants import (
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
    STATUS_ARRIVED_DESTINATION,
    STATUS_RECEIVED,
)


def _normalize_status_code(status_code: str | None) -> str:
    raw = (status_code or "").strip()
    normalized = raw.lower().strip()

    aliases = {
        # China warehouse
        STATUS_CHINA_RECEIVED: STATUS_CHINA_RECEIVED,
        "china_received": STATUS_CHINA_RECEIVED,
        "china": STATUS_CHINA_RECEIVED,
        "in_china": STATUS_CHINA_RECEIVED,
        "china_warehouse": STATUS_CHINA_RECEIVED,
        "dar_skladi_chin": STATUS_CHINA_RECEIVED,
        "дар склади чин": STATUS_CHINA_RECEIVED,
        "дар склади Чин": STATUS_CHINA_RECEIVED,

        # On the way
        STATUS_ON_THE_WAY: STATUS_ON_THE_WAY,
        "on_the_way": STATUS_ON_THE_WAY,
        "onway": STATUS_ON_THE_WAY,
        "in_transit": STATUS_ON_THE_WAY,
        "dar_rah": STATUS_ON_THE_WAY,
        "дар роҳ": STATUS_ON_THE_WAY,

        # Arrived destination
        STATUS_ARRIVED_DESTINATION: STATUS_ARRIVED_DESTINATION,
        "arrived_destination": STATUS_ARRIVED_DESTINATION,
        "arrived": STATUS_ARRIVED_DESTINATION,
        "arrived_tj": STATUS_ARRIVED_DESTINATION,
        "ba_sklad_rasid": STATUS_ARRIVED_DESTINATION,
        "ба склад расид": STATUS_ARRIVED_DESTINATION,

        # Received / delivered
        STATUS_RECEIVED: STATUS_RECEIVED,
        "received": STATUS_RECEIVED,
        "delivered": STATUS_RECEIVED,
        "suporida_shud": STATUS_RECEIVED,
        "супорида шуд": STATUS_RECEIVED,
    }

    return aliases.get(raw) or aliases.get(normalized) or normalized


STATUS_IMAGE_KEYS = {
    STATUS_CHINA_RECEIVED: "status_image_china_received_file_id",
    STATUS_ON_THE_WAY: "status_image_on_the_way_file_id",
    STATUS_ARRIVED_DESTINATION: "status_image_arrived_destination_file_id",
    STATUS_RECEIVED: "status_image_received_file_id",
}


async def get_status_image_file_id(status_code: str | None) -> str:
    normalized_status = _normalize_status_code(status_code)
    key = STATUS_IMAGE_KEYS.get(normalized_status)

    defaults = {
        "status_image_file_id": "",
    }

    if key:
        defaults[key] = ""

    values = await get_many_settings(defaults)

    if key:
        specific = (values.get(key) or "").strip()
        if specific:
            return specific

    fallback = (values.get("status_image_file_id") or "").strip()
    return fallback
