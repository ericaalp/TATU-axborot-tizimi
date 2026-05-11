from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import SUPERADMIN_IDS
from db import get_user, create_user
from keyboards import asosiy_menu_kb, admin_menu_kb, telefon_kb, remove_kb
from states import Royxat

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, pool):
    await state.clear()
    telegram_id = message.from_user.id

    # Superadmin tekshiruvi
    if telegram_id in SUPERADMIN_IDS:
        await message.answer(
            "👋 Xush kelibsiz, Admin!\n\nAdmin panel ochildi.",
            reply_markup=admin_menu_kb()
        )
        return

    # Qaytgan foydalanuvchi
    user = await get_user(pool, telegram_id)
    if user:
        await message.answer(
            f"👋 Xush kelibsiz, <b>{user['ism']}</b>!\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=asosiy_menu_kb()
        )
        return

    # Yangi foydalanuvchi — ro'yxatdan o'tkazish
    await message.answer(
        "👋 Assalomu alaykum! TATU SF botiga xush kelibsiz.\n\n"
        "Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
        "Ismingizni kiriting:",
        reply_markup=remove_kb()
    )
    await state.set_state(Royxat.ism)


@router.message(Royxat.ism)
async def royxat_ism(message: Message, state: FSMContext):
    ism = message.text.strip()
    if len(ism) < 2:
        await message.answer("❌ Ism kamida 2 ta harf bo'lishi kerak. Qayta kiriting:")
        return
    await state.update_data(ism=ism)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Royxat.familiya)


@router.message(Royxat.familiya)
async def royxat_familiya(message: Message, state: FSMContext):
    familiya = message.text.strip()
    if len(familiya) < 2:
        await message.answer("❌ Familiya kamida 2 ta harf bo'lishi kerak. Qayta kiriting:")
        return
    await state.update_data(familiya=familiya)
    await message.answer(
        "📱 Telefon raqamingizni ulashing:\n"
        "<i>(Quyidagi tugmani bosing)</i>",
        reply_markup=telefon_kb()
    )
    await state.set_state(Royxat.telefon)


@router.message(Royxat.telefon, F.contact)
async def royxat_telefon(message: Message, state: FSMContext):
    tel = message.contact.phone_number
    if not tel.startswith("+"):
        tel = "+" + tel
    await state.update_data(tel_raqam=tel)

    data = await state.get_data()
    await message.answer(
        f"✅ Ma'lumotlaringiz:\n\n"
        f"👤 Ism: <b>{data['ism']}</b>\n"
        f"👤 Familiya: <b>{data['familiya']}</b>\n"
        f"📞 Telefon: <b>{tel}</b>\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=remove_kb()
    )
    await state.set_state(Royxat.tasdiqlash)


@router.message(Royxat.telefon)
async def royxat_telefon_xato(message: Message):
    await message.answer(
        "❌ Iltimos, quyidagi tugma orqali raqamingizni ulashing:",
        reply_markup=telefon_kb()
    )


@router.message(Royxat.tasdiqlash)
async def royxat_tasdiqlash(message: Message, state: FSMContext, pool):
    matn = message.text.strip().lower()
    if matn in ("ha", "yes", "✅", "tasdiqlayman"):
        data = await state.get_data()
        user_id = await create_user(
            pool,
            telegram_id=message.from_user.id,
            telegram_username=message.from_user.username,
            ism=data["ism"],
            familiya=data["familiya"],
            tel_raqam=data["tel_raqam"],
        )
        await state.clear()
        if user_id:
            await message.answer(
                f"✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
                f"Xush kelibsiz, <b>{data['ism']}</b>!",
                reply_markup=asosiy_menu_kb()
            )
        else:
            await message.answer(
                "✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\nXush kelibsiz!",
                reply_markup=asosiy_menu_kb()
            )
    else:
        await message.answer(
            "Tasdiqlash uchun <b>Ha</b> deb yozing yoki botni qayta ishga tushiring /start"
        )
