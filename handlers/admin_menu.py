from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.reply import admin_main_menu
from utils.validators import is_admin


router = Router(name="admin_menu")


ACCESS_DENIED = "⛔ Дастрасӣ иҷозат нест."
ADMIN_PANEL = "⚙️ Панели админ"


@router.message(Command("admin"))
async def admin_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer(ACCESS_DENIED)
        return

    await message.answer(ADMIN_PANEL, reply_markup=admin_main_menu())
