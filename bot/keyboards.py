# bot/keyboards.py
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def confirm_proposal_kb(proposal_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"confirm:{proposal_id}")
    kb.button(text="❌ Отменить", callback_data=f"cancel:{proposal_id}")
    kb.adjust(2)
    return kb.as_markup()