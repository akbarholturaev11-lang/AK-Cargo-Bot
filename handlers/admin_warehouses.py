from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline_admin import (
    admin_warehouse_city_keyboard,
    warehouse_management_keyboard,
    warehouse_preview_keyboard,
)
from services.warehouses import (
    list_warehouses,
    save_active_warehouse,
    save_tj_pickup_warehouse,
    set_warehouse_inactive,
)
from states.admin_warehouse_states import AdminWarehouseStates
from utils.constants import CITY_NAMES, LANG_TJ
from utils.validators import is_admin


router = Router(name="admin_warehouses")


WAREHOUSE_BLOCK_PROMPT = "Сурати адрес, видео ё матни тайёрро равон кунед."


def _is_admin_message(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _is_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)


def _city_name(city_key: str) -> str:
    return CITY_NAMES[city_key][LANG_TJ]


async def _show_preview(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(AdminWarehouseStates.confirming)
    media_type = data["media_type"]
    media_file_id = data.get("media_file_id")
    caption = data["address_caption"]

    if data.get("address_kind") == "tj_pickup":
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Сабт кардан", callback_data="admin_wh:save_tj_pickup")],
                [InlineKeyboardButton(text="Матнро иваз кардан", callback_data="admin_wh:change_caption")],
                [InlineKeyboardButton(text="Медиаро иваз кардан", callback_data="admin_wh:change_media")],
                [InlineKeyboardButton(text="Бекор кардан", callback_data="admin_wh:cancel")],
            ]
        )
    else:
        keyboard = warehouse_preview_keyboard()

    if media_type == "photo" and media_file_id:
        await message.answer_photo(
            photo=media_file_id,
            caption=caption,
            reply_markup=keyboard,
        )
        return

    if media_type == "video" and media_file_id:
        await message.answer_video(
            video=media_file_id,
            caption=caption,
            reply_markup=keyboard,
        )
        return

    await message.answer(caption, reply_markup=keyboard)


async def _finish_preview(callback: CallbackQuery, text: str) -> None:
    if callback.message is None:
        return

    if callback.message.photo or callback.message.video:
        await callback.message.edit_caption(caption=text, reply_markup=None)
        return

    await callback.message.answer(text, reply_markup=None)


async def _prompt_tj_pickup_after_china_address(
    callback: CallbackQuery,
    state: FSMContext,
    warehouse,
) -> None:
    await state.update_data(
        address_kind="tj_pickup",
        city_key=warehouse.city_key,
        media_type="text",
        media_file_id=None,
        address_caption="",
    )
    await state.set_state(AdminWarehouseStates.waiting_for_photo_caption)

    if callback.message is not None:
        await callback.message.answer(
            "✅ <b>Адреси склади Чин сабт шуд.</b>\n\n"
            f"<blockquote>Филиал: {warehouse.city_name_tj}</blockquote>\n\n"
            "🇹🇯 <b>Акнун адреси гирифтани бор дар Тоҷикистонро илова кунед.</b>\n\n"
            "<blockquote>"
            "Фото + caption, видео + caption ё матни одӣ фиристед.\n"
            "Ин адрес вақте нишон дода мешавад, ки user <b>Аз склад гирифтан</b>-ро пахш кунад."
            "</blockquote>"
        )


@router.callback_query(F.data == "settings:warehouses")
async def show_warehouse_settings(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    if callback.message is not None:
        await callback.message.answer(
            "Складҳо",
            reply_markup=warehouse_management_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data.in_({"admin_wh:add", "admin_wh:edit"}))
async def start_add_or_edit_warehouse(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    action = callback.data.rsplit(":", 1)[1]
    await state.clear()
    await state.update_data(action=action)
    await state.set_state(AdminWarehouseStates.choosing_city)

    if callback.message is not None:
        await callback.message.answer(
            "Шаҳрро интихоб кунед.",
            reply_markup=admin_warehouse_city_keyboard(action),
        )
    await callback.answer()


@router.callback_query(F.data == "admin_wh:inactive")
async def start_inactive_warehouse(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    await state.set_state(AdminWarehouseStates.choosing_inactive_city)
    if callback.message is not None:
        await callback.message.answer(
            "Ғайрифаъол кардан: шаҳрро интихоб кунед.",
            reply_markup=admin_warehouse_city_keyboard("inactive"),
        )
    await callback.answer()


@router.callback_query(F.data == "admin_wh:list")
async def list_admin_warehouses(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    warehouses = await list_warehouses()
    if not warehouses:
        text = "Склад сабт нашудааст."
    else:
        lines = ["Рӯйхати складҳо:"]
        for warehouse in warehouses:
            status = "фаъол" if warehouse.is_active else "ғайрифаъол"
            lines.append(
                f"{warehouse.city_name_tj}: {status} · ID {warehouse.id}",
            )
        text = "\n".join(lines)

    if callback.message is not None:
        await callback.message.answer(
            text,
            reply_markup=warehouse_management_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.choosing_city,
    (
        F.data.startswith("admin_wh:city:add:")
        | F.data.startswith("admin_wh:city:edit:")
    ),
)
async def choose_warehouse_city(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer()
        return

    city_key = parts[3]
    if city_key not in CITY_NAMES:
        await callback.answer()
        return

    await state.update_data(city_key=city_key, city_name=_city_name(city_key))
    await state.set_state(AdminWarehouseStates.waiting_for_photo_caption)
    if callback.message is not None:
        await callback.message.answer(WAREHOUSE_BLOCK_PROMPT)
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.choosing_inactive_city,
    F.data.startswith("admin_wh:city:inactive:"),
)
async def inactive_warehouse_city(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    city_key = callback.data.rsplit(":", 1)[1]
    if city_key not in CITY_NAMES:
        await callback.answer()
        return

    count = await set_warehouse_inactive(city_key)
    await state.clear()
    if callback.message is not None:
        await callback.message.answer(
            f"{_city_name(city_key)} ғайрифаъол шуд. Сабтҳо: {count}",
            reply_markup=warehouse_management_keyboard(),
        )
    await callback.answer()


@router.message(AdminWarehouseStates.waiting_for_photo_caption, F.photo)
async def receive_warehouse_photo_caption(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    if not message.caption:
        await message.answer("Матн лозим аст. Суратро бо матн фиристед.")
        return

    await state.update_data(
        media_type="photo",
        media_file_id=message.photo[-1].file_id,
        address_caption=message.caption,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo_caption, F.video)
async def receive_warehouse_video_caption(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    if not message.caption:
        await message.answer("Матн лозим аст. Видеоро бо матн фиристед.")
        return

    await state.update_data(
        media_type="video",
        media_file_id=message.video.file_id,
        address_caption=message.caption,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo_caption, F.text)
async def receive_warehouse_text(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    text = message.text.strip()
    if not text:
        await message.answer(WAREHOUSE_BLOCK_PROMPT)
        return

    await state.update_data(
        media_type="text",
        media_file_id=None,
        address_caption=text,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo_caption)
async def receive_warehouse_photo_caption_invalid(message: Message) -> None:
    if not _is_admin_message(message):
        return

    await message.answer(WAREHOUSE_BLOCK_PROMPT)


@router.callback_query(AdminWarehouseStates.confirming, F.data == "admin_wh:save")
async def save_warehouse(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    data = await state.get_data()
    warehouse = await save_active_warehouse(
        city_key=data["city_key"],
        media_type=data["media_type"],
        media_file_id=data.get("media_file_id"),
        address_caption=data["address_caption"],
    )
    has_tj_pickup = bool(
        (getattr(warehouse, "tj_pickup_caption", None) or "").strip()
        or (getattr(warehouse, "tj_pickup_media_file_id", None) or "").strip()
    )

    if not has_tj_pickup:
        await _prompt_tj_pickup_after_china_address(callback, state, warehouse)
        await callback.answer()
        return

    await state.clear()
    await _finish_preview(
        callback,
        (
            "Склад сабт шуд.\n"
            f"Шаҳр: {warehouse.city_name_tj}\n"
            f"Статус: фаъол"
        ),
    )
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.confirming,
    F.data == "admin_wh:change_caption",
)
async def change_warehouse_caption(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.set_state(AdminWarehouseStates.waiting_for_caption)
    if callback.message is not None:
        await callback.message.answer("Матни навро фиристед.")
    await callback.answer()


@router.message(AdminWarehouseStates.waiting_for_caption, F.text)
async def receive_new_caption(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.update_data(address_caption=message.text)
    await _show_preview(message, state)


@router.callback_query(
    AdminWarehouseStates.confirming,
    F.data == "admin_wh:change_media",
)
async def change_warehouse_media(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.set_state(AdminWarehouseStates.waiting_for_photo)
    if callback.message is not None:
        await callback.message.answer("Медиаи навро фиристед.")
    await callback.answer()


@router.message(AdminWarehouseStates.waiting_for_photo, F.photo)
async def receive_new_photo(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    data = await state.get_data()
    caption = message.caption or data["address_caption"]
    await state.update_data(
        media_type="photo",
        media_file_id=message.photo[-1].file_id,
        address_caption=caption,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo, F.video)
async def receive_new_video(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    data = await state.get_data()
    caption = message.caption or data["address_caption"]
    await state.update_data(
        media_type="video",
        media_file_id=message.video.file_id,
        address_caption=caption,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo, F.text)
async def receive_new_text_block(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    text = message.text.strip()
    if not text:
        await message.answer(WAREHOUSE_BLOCK_PROMPT)
        return

    await state.update_data(
        media_type="text",
        media_file_id=None,
        address_caption=text,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo)
async def receive_new_media_invalid(message: Message) -> None:
    if not _is_admin_message(message):
        return

    await message.answer(WAREHOUSE_BLOCK_PROMPT)


@router.callback_query(AdminWarehouseStates.confirming, F.data == "admin_wh:resend")
async def resend_warehouse_block(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.set_state(AdminWarehouseStates.waiting_for_photo_caption)
    if callback.message is not None:
        await callback.message.answer(WAREHOUSE_BLOCK_PROMPT)
    await callback.answer()


@router.callback_query(F.data == "admin_wh:cancel")
async def cancel_warehouse_flow(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    if callback.message is not None:
        if callback.message.photo or callback.message.video:
            await callback.message.edit_caption("Амалиёт бекор карда шуд.")
        else:
            await callback.message.answer("Амалиёт бекор карда шуд.")
    await callback.answer()


@router.callback_query(F.data == "admin_wh:tj_pickup")
async def start_tj_pickup_warehouse(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    await state.update_data(address_kind="tj_pickup")
    await state.set_state(AdminWarehouseStates.choosing_city)

    if callback.message is not None:
        await callback.message.answer(
            "🇹🇯 <b>Адреси гирифтани бор</b>\n\n"
            "<blockquote>Филиалро интихоб кунед. Ин адрес вақте ба user нишон дода мешавад, ки бораш ба Тоҷикистон расида бошад.</blockquote>",
            reply_markup=admin_warehouse_city_keyboard("tj_pickup"),
        )
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.choosing_city,
    F.data.startswith("admin_wh:city:tj_pickup:")
)
async def choose_tj_pickup_city(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    city_key = callback.data.split(":")[-1]
    if city_key not in CITY_NAMES:
        await callback.answer()
        return

    await state.update_data(city_key=city_key, address_kind="tj_pickup")
    await state.set_state(AdminWarehouseStates.waiting_for_photo_caption)

    if callback.message is not None:
        await callback.message.answer(
            "🇹🇯 <b>Адреси гирифтани бор</b>\n\n"
            "<blockquote>"
            "Фото + caption, видео + caption ё матни одӣ фиристед.\n\n"
            "Ин адрес вақте нишон дода мешавад, ки user <b>Аз склад гирифтан</b>-ро пахш кунад."
            "</blockquote>"
        )
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.confirming,
    F.data == "admin_wh:save_tj_pickup"
)
async def save_tj_pickup(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    data = await state.get_data()

    warehouse = await save_tj_pickup_warehouse(
        city_key=data["city_key"],
        media_type=data["media_type"],
        media_file_id=data.get("media_file_id"),
        caption=data["address_caption"],
    )

    await state.clear()

    await _finish_preview(
        callback,
        (
            "✅ Адреси гирифтани бор сабт шуд.\n"
            f"Филиал: {warehouse.city_name_tj}"
        ),
    )
    await callback.answer()
