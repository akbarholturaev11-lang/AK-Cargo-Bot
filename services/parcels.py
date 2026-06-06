from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from database.db import async_session
from database.models import Parcel
from services.airtable_sync import (
    sync_daily_stats_to_airtable,
    sync_parcel_to_airtable,
    sync_parcels_to_airtable,
)
from utils.constants import STATUS_CHINA_RECEIVED


async def get_parcel_by_normalized_track_code(
    normalized_track_code: str,
) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel).where(
                Parcel.normalized_track_code == normalized_track_code,
            ),
        )
        return result.scalar_one_or_none()


async def get_parcel_with_user_by_normalized_track_code(
    normalized_track_code: str,
) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(Parcel.normalized_track_code == normalized_track_code),
        )
        return result.scalar_one_or_none()


async def get_parcel_with_user(parcel_id: int) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(Parcel.id == parcel_id),
        )
        return result.scalar_one_or_none()


async def get_parcel_for_user(parcel_id: int, user_id: int) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel).where(
                Parcel.id == parcel_id,
                Parcel.user_id == user_id,
            ),
        )
        return result.scalar_one_or_none()


async def get_parcels_by_client_code(client_code: str) -> list[Parcel]:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .where(Parcel.client_code == client_code)
            .order_by(Parcel.received_china_at.desc(), Parcel.id.desc()),
        )
        return list(result.scalars().all())


async def get_parcels_with_user_by_client_code(client_code: str) -> list[Parcel]:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(Parcel.client_code == client_code)
            .order_by(Parcel.received_china_at.desc(), Parcel.id.desc()),
        )
        return list(result.scalars().all())


async def list_parcels_by_status(
    *,
    status_code: str,
    limit: int,
    offset: int = 0,
) -> list[Parcel]:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(Parcel.status_code == status_code)
            .order_by(Parcel.created_at.desc(), Parcel.id.desc())
            .offset(offset)
            .limit(limit),
        )
        return list(result.scalars().all())


async def count_parcels_by_status(status_code: str) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.count(Parcel.id)).where(Parcel.status_code == status_code),
        )
        return int(result.scalar_one())


async def create_parcel(
    *,
    track_code: str,
    normalized_track_code: str,
    client_code: str,
    user_id: int,
    destination_city: str,
    received_china_at: datetime,
    created_by_admin_id: int | None,
) -> Parcel:
    async with async_session() as session:
        parcel = Parcel(
            track_code=track_code,
            normalized_track_code=normalized_track_code,
            client_code=client_code,
            user_id=user_id,
            destination_city=destination_city,
            status_code=STATUS_CHINA_RECEIVED,
            received_china_at=received_china_at,
            batch_date=received_china_at.date(),
            created_by_admin_id=created_by_admin_id,
        )
        session.add(parcel)
        await session.commit()
        await session.refresh(parcel)
        parcel_id = parcel.id
        stats_date = parcel.received_china_at.date()

    await sync_parcel_to_airtable(parcel_id)
    await sync_daily_stats_to_airtable(stats_date)
    return parcel


async def mark_china_received_notified(parcel_id: int) -> Parcel | None:
    sync_needed = False
    async with async_session() as session:
        parcel = await session.get(Parcel, parcel_id)
        if parcel is None:
            return None

        if parcel.china_received_notified_at is None:
            parcel.china_received_notified_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(parcel)
            sync_needed = True

    if sync_needed:
        await sync_parcel_to_airtable(parcel_id)
    return parcel


async def update_parcel_status(parcel_id: int, status_code: str) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(Parcel.id == parcel_id),
        )
        parcel = result.scalar_one_or_none()
        if parcel is None:
            return None

        parcel.status_code = status_code
        parcel.updated_at = datetime.now(timezone.utc)
        await session.commit()
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(Parcel.id == parcel_id),
        )
        parcel = result.scalar_one_or_none()
        stats_date = parcel.updated_at.date() if parcel is not None else None

    if parcel is not None:
        await sync_parcel_to_airtable(parcel.id)
        if stats_date is not None:
            await sync_daily_stats_to_airtable(stats_date)
    return parcel


async def mark_arrival_notified(parcel_id: int) -> Parcel | None:
    sync_needed = False
    async with async_session() as session:
        parcel = await session.get(Parcel, parcel_id)
        if parcel is None:
            return None

        if parcel.arrival_notified_at is None:
            parcel.arrival_notified_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(parcel)
            sync_needed = True

    if sync_needed:
        await sync_parcel_to_airtable(parcel_id)
    return parcel


async def count_parcels_for_bulk_status_update(
    *,
    destination_city: str,
    batch_date: date,
    old_status: str,
) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel.id).where(
                Parcel.destination_city == destination_city,
                Parcel.batch_date == batch_date,
                Parcel.status_code == old_status,
            ),
        )
        return len(result.scalars().all())


async def bulk_update_parcel_status(
    *,
    destination_city: str,
    batch_date: date,
    old_status: str,
    new_status: str,
) -> list[Parcel]:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(
                Parcel.destination_city == destination_city,
                Parcel.batch_date == batch_date,
                Parcel.status_code == old_status,
            ),
        )
        parcels = list(result.scalars().all())
        now = datetime.now(timezone.utc)

        for parcel in parcels:
            parcel.status_code = new_status
            parcel.updated_at = now

        await session.commit()
        parcel_ids = [parcel.id for parcel in parcels]
        stats_date = now.date()

    await sync_parcels_to_airtable(parcel_ids)
    await sync_daily_stats_to_airtable(stats_date)
    return parcels
