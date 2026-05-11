from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import (
    get_kafedralar_by_bino, get_kafedra, get_kafedra_oqituvchilari,
    get_oqituvchi, get_oqituvchi_bugungi_dars, get_oqituvchi_by_search,
    get_qavat_xonalari, get_xona_tafsilot, get_xona_bugungi_jadval, log_sorov,
    JUFT_VAQTLAR, hozirgi_juft,
)
from keyboards import (
    binolar_inline_kb, kafedralar_inline_kb, oqituvchilar_inline_kb,
    oqituvchi_nav_kb, qidiruv_natijalari_kb, asosiy_menu_kb,
)
from states import Qidiruv

KUNLAR = {0: 'dushanba', 1: 'seshanba', 2: 'chorshanba', 3: 'payshanba', 4: 'juma'}
AJRATGICH = '━' * 24

router = Router()


# ─── O'qituvchi kartasi formati ───────────────────────────────────────────────

def format_oqituvchi_karta(oqituvchi: dict, darslar: list[dict]) -> str:
    o = oqituvchi

    ism_toliq = f"{o['familiya']} {o['ism']}"
    if o.get("otasining_ismi"):
        ism_toliq += f" {o['otasining_ismi']}"

    qatorlar = [AJRATGICH, f"👤 {ism_toliq}", ""]

    if o.get("kafedra_nomi"):
        qatorlar.append(f"🏫 Kafedra: {o['kafedra_nomi']}")

    if o.get("xona_raqam") and o.get("bino"):
        qatorlar.append(f"🏢 Xona: {o['xona_raqam']}, {o['bino']}-bino")

    tel = o.get("tel_raqam") or ""
    qatorlar.append(f"📞 Tel: {tel or 'koʼrsatilmagan'}")

    tg = o.get("telegram_username") or ""
    tg_text = f"@{tg.lstrip('@')}" if tg else "koʼrsatilmagan"
    qatorlar.append(f"✈️ Telegram: {tg_text}")

    qatorlar.append("")

    bugun_index = datetime.now().weekday()

    if bugun_index >= 5:
        qatorlar.append("📅 Bugun dam olish kuni.")
        _qosh_kafedra_xona(qatorlar, o)
    elif darslar:
        bugun_nomi = KUNLAR[bugun_index].capitalize()
        qatorlar.append(f"📅 Bugun ({bugun_nomi}):")
        qatorlar.append("")
        for i, d in enumerate(darslar):
            bosh = str(d["boshlanish"])[:5]
            tug  = str(d["tugash"])[:5]
            qatorlar.append(f"⏰ {bosh}–{tug}")
            qatorlar.append(f"📍 {d['xona_raqam']}-xona, {d['bino']}-bino")
            qatorlar.append(d["fan_nomi"])
            if d.get("guruh"):
                qatorlar.append(d["guruh"])
            if i < len(darslar) - 1:
                qatorlar.append("")
    else:
        qatorlar.append("📅 Bugun dars yoʼq.")
        _qosh_kafedra_xona(qatorlar, o)

    qatorlar.append(AJRATGICH)
    return "\n".join(qatorlar)


def _qosh_kafedra_xona(qatorlar: list, o: dict) -> None:
    kx = o.get("kafedra_xona_raqam")
    kb = o.get("kafedra_bino")
    if kx and kb:
        qatorlar.append("🏢 Kafedra xonasida boʼlishi mumkin:")
        qatorlar.append(f"{kx}-xona, {kb}-bino")


# ─── Kafedralar ──────────────────────────────────────────────────────────────

@router.message(F.text == "🏛 Kafedralar")
async def kafedralar_menu(message: Message, pool):
    await log_sorov(pool, message.from_user.id, "Kafedralar")
    await message.answer("Binoni tanlang:", reply_markup=binolar_inline_kb())


@router.callback_query(F.data == "binolar")
async def cb_binolar(call: CallbackQuery):
    await call.message.edit_text("Binoni tanlang:", reply_markup=binolar_inline_kb())
    await call.answer()


@router.callback_query(F.data.startswith("bino:"))
async def cb_bino(call: CallbackQuery, pool):
    bino = call.data.split(":")[1]
    kafedralar = await get_kafedralar_by_bino(pool, bino)
    if not kafedralar:
        await call.answer("Kafedralar topilmadi", show_alert=True)
        return
    matn = f"🏢 <b>{bino}-bino</b> kafedralari:"
    await call.message.edit_text(matn, reply_markup=kafedralar_inline_kb(kafedralar, bino))
    await call.answer()


@router.callback_query(F.data.startswith("kafedra:"))
async def cb_kafedra(call: CallbackQuery, pool):
    kafedra_id = int(call.data.split(":")[1])
    kafedra = await get_kafedra(pool, kafedra_id)
    oqituvchilar = await get_kafedra_oqituvchilari(pool, kafedra_id)
    if not kafedra:
        await call.answer("Kafedra topilmadi", show_alert=True)
        return
    bino_text = f"{kafedra['bino']}-bino" if kafedra.get("bino") else ""
    xona_text = f", {kafedra['xona_raqam']}-xona" if kafedra.get("xona_raqam") else ""
    matn = (
        f"📌 <b>{kafedra['nomi']}</b>\n"
        f"🏢 {bino_text}{xona_text}\n\n"
        f"O'qituvchilardan birini tanlang:"
    )
    await call.message.edit_text(matn, reply_markup=oqituvchilar_inline_kb(oqituvchilar, kafedra_id))
    await call.answer()


@router.callback_query(F.data.startswith("kafedralar:"))
async def cb_kafedralar(call: CallbackQuery, pool):
    # kafedra_id orqali bino aniqlanadi
    kafedra_id = int(call.data.split(":")[1])
    kafedra = await get_kafedra(pool, kafedra_id)
    if kafedra and kafedra.get("bino"):
        bino = kafedra["bino"]
        kafedralar = await get_kafedralar_by_bino(pool, bino)
        matn = f"🏢 <b>{bino}-bino</b> kafedralari:"
        await call.message.edit_text(matn, reply_markup=kafedralar_inline_kb(kafedralar, bino))
    else:
        await call.message.edit_text("Binoni tanlang:", reply_markup=binolar_inline_kb())
    await call.answer()


@router.callback_query(F.data.startswith("kafedraga:"))
async def cb_kafedraga(call: CallbackQuery, pool):
    kafedra_id = int(call.data.split(":")[1])
    kafedra = await get_kafedra(pool, kafedra_id)
    oqituvchilar = await get_kafedra_oqituvchilari(pool, kafedra_id)
    if not kafedra:
        await call.answer("Kafedra topilmadi", show_alert=True)
        return
    bino_text = f"{kafedra['bino']}-bino" if kafedra.get("bino") else ""
    xona_text = f", {kafedra['xona_raqam']}-xona" if kafedra.get("xona_raqam") else ""
    matn = (
        f"📌 <b>{kafedra['nomi']}</b>\n"
        f"🏢 {bino_text}{xona_text}\n\n"
        f"O'qituvchilardan birini tanlang:"
    )
    await call.message.edit_text(matn, reply_markup=oqituvchilar_inline_kb(oqituvchilar, kafedra_id))
    await call.answer()


@router.callback_query(F.data.startswith("oqituvchi:"))
async def cb_oqituvchi(call: CallbackQuery, pool):
    oqituvchi_id = int(call.data.split(":")[1])
    await _karta_korsatish(call, pool, oqituvchi_id)


@router.callback_query(F.data.startswith("qidiruv:"))
async def cb_qidiruv_karta(call: CallbackQuery, pool):
    oqituvchi_id = int(call.data.split(":")[1])
    await _karta_korsatish(call, pool, oqituvchi_id)


async def _karta_korsatish(call: CallbackQuery, pool, oqituvchi_id: int):
    o = await get_oqituvchi(pool, oqituvchi_id)
    if not o:
        await call.answer("O'qituvchi topilmadi", show_alert=True)
        return

    darslar = await get_oqituvchi_bugungi_dars(pool, oqituvchi_id)
    matn = format_oqituvchi_karta(o, darslar)

    await call.message.edit_text(
        matn,
        reply_markup=oqituvchi_nav_kb(o.get("kafedra_id", 0), o.get("telegram_file_id")),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("rasm:"))
async def cb_rasm(call: CallbackQuery):
    file_id = call.data.split(":", 1)[1]
    await call.message.answer_photo(photo=file_id)
    await call.answer()


# ─── Xona holati ─────────────────────────────────────────────────────────────

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def _xona_bino_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏢 A-bino", callback_data="xona_bino:A"),
        InlineKeyboardButton(text="🏢 B-bino", callback_data="xona_bino:B"),
    ]])


def _xona_qavat_kb(bino: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="1-qavat", callback_data=f"xona_qavat:{bino}:1"),
        InlineKeyboardButton(text="2-qavat", callback_data=f"xona_qavat:{bino}:2"),
        InlineKeyboardButton(text="3-qavat", callback_data=f"xona_qavat:{bino}:3"),
    ], [
        InlineKeyboardButton(text="◀️ Binolar", callback_data="xona_holati_menu"),
    ]])


def _xona_rooms_kb(xonalar: list[dict], bino: str, qavat: int) -> InlineKeyboardMarkup:
    rows = []
    qator = []
    for x in xonalar:
        belgi = "🔴" if x['holat'] == 'band' else "✅"
        qator.append(InlineKeyboardButton(
            text=f"{belgi}{x['raqam']}",
            callback_data=f"xona_detail:{x['raqam']}:{bino}",
        ))
        if len(qator) == 4:
            rows.append(qator)
            qator = []
    if qator:
        rows.append(qator)
    rows.append([InlineKeyboardButton(
        text="◀️ Qavatlar",
        callback_data=f"xona_bino:{bino}",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _xona_detail_kb(teachers: list[dict], bino: str, qavat: int) -> InlineKeyboardMarkup:
    rows = []
    seen = set()
    for d in teachers:
        oq_id = d.get('oqituvchi_id')
        if oq_id and oq_id not in seen:
            seen.add(oq_id)
            oq = f"{d['familiya']} {d['ism'][:1]}."
            rows.append([InlineKeyboardButton(
                text=f"👤 {oq} haqida",
                callback_data=f"oqituvchi:{oq_id}",
            )])
    rows.append([InlineKeyboardButton(
        text="◀️ Xonalarga qaytish",
        callback_data=f"xona_qavat:{bino}:{qavat}",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(F.text == "🚪 Xona holati")
async def xona_holati_menu(message: Message, pool):
    await log_sorov(pool, message.from_user.id, "Xona holati")
    await message.answer("🏢 Binoni tanlang:", reply_markup=_xona_bino_kb())


@router.callback_query(F.data == "xona_holati_menu")
async def cb_xona_holati_menu(call: CallbackQuery):
    await call.message.edit_text("🏢 Binoni tanlang:", reply_markup=_xona_bino_kb())
    await call.answer()


@router.callback_query(F.data.startswith("xona_bino:"))
async def cb_xona_bino(call: CallbackQuery):
    bino = call.data.split(":")[1]
    await call.message.edit_text(
        f"🏢 <b>{bino}-bino</b> — qavatni tanlang:",
        reply_markup=_xona_qavat_kb(bino),
    )
    await call.answer()


@router.callback_query(F.data.startswith("xona_qavat:"))
async def cb_xona_qavat(call: CallbackQuery, pool):
    parts = call.data.split(":")
    bino = parts[1]
    qavat = int(parts[2])
    xonalar = await get_qavat_xonalari(pool, bino, qavat)
    if not xonalar:
        await call.message.edit_text(
            f"ℹ️ {bino}-bino {qavat}-qavatda xonalar topilmadi.",
            reply_markup=_xona_qavat_kb(bino),
        )
        await call.answer()
        return
    matn = f"🏢 <b>{bino}-bino, {qavat}-qavat</b>\n✅ bo'sh  🔴 band"
    await call.message.edit_text(matn, reply_markup=_xona_rooms_kb(xonalar, bino, qavat))
    await call.answer()


@router.callback_query(F.data.startswith("xona_detail:"))
async def cb_xona_detail(call: CallbackQuery, pool):
    parts = call.data.split(":")
    raqam = int(parts[1])
    bino = parts[2]

    xona = await get_xona_tafsilot(pool, raqam, bino)
    darslar = await get_xona_bugungi_jadval(pool, raqam, bino)

    qavat = xona['qavat'] if xona else 1
    hozirgi = hozirgi_juft()
    dars_by_juft = {d['juft_raqami']: d for d in darslar if d.get('juft_raqami')}

    # Hozirgi holat
    if hozirgi and hozirgi in dars_by_juft:
        hozirgi_holat = "🔴 Band"
    elif xona and xona.get('band'):
        hozirgi_holat = "🔴 Band (qo'lda)"
    else:
        hozirgi_holat = "✅ Bo'sh"

    matn = f"🏢 <b>{bino}-bino, {raqam}-xona</b>\n"
    matn += f"Hozirgi holat: {hozirgi_holat}\n"
    matn += "\n📅 <b>Bugungi dars jadvali:</b>"

    band_teachers = []
    for j_n, (bosh, tug) in JUFT_VAQTLAR.items():
        d = dars_by_juft.get(j_n)
        hozir_belgisi = " ◀" if hozirgi == j_n else ""
        matn += f"\n\n<b>{j_n}-juft</b> {bosh}–{tug}{hozir_belgisi}"
        if d:
            oq = f"{d['familiya']} {d['ism']}".strip()
            guruh = d.get('guruh') or '—'
            matn += f"\n🔴 BAND\n👤 {oq}\n{d['fan_nomi']}\n{guruh} guruhi"
            band_teachers.append(d)
        else:
            matn += "\n✅ BO'SH"

    await call.message.edit_text(
        matn,
        reply_markup=_xona_detail_kb(band_teachers, bino, qavat),
    )
    await call.answer()


# ─── Domla qidirish ──────────────────────────────────────────────────────────

@router.message(F.text == "🔍 Domla qidirish")
async def domla_qidirish(message: Message, state: FSMContext, pool):
    await log_sorov(pool, message.from_user.id, "Domla qidirish")
    await message.answer(
        "🔍 O'qituvchi ism yoki familiyasini kiriting:",
        reply_markup=asosiy_menu_kb()
    )
    await state.set_state(Qidiruv.ism_kiritish)


@router.callback_query(F.data == "qidiruv_boshla")
async def cb_qidiruv_boshla(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "🔍 O'qituvchi ism yoki familiyasini kiriting:",
        reply_markup=asosiy_menu_kb()
    )
    await state.set_state(Qidiruv.ism_kiritish)
    await call.answer()


@router.message(Qidiruv.ism_kiritish)
async def qidiruv_natija(message: Message, state: FSMContext, pool):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("❌ Kamida 2 ta harf kiriting:")
        return

    # Qidiruv natijasiga kafedra nomi ham kerak
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT o.*, k.nomi AS kafedra_nomi
               FROM oqituvchilar o
               LEFT JOIN kafedralar k ON k.id = o.kafedra_id
               WHERE (o.familiya ILIKE $1 OR o.ism ILIKE $1) AND o.faol = TRUE
               ORDER BY o.familiya
               LIMIT 5""",
            f"%{query}%"
        )
    oqituvchilar = [dict(r) for r in rows]

    if not oqituvchilar:
        await message.answer(
            f"❌ <b>{query}</b> bo'yicha o'qituvchi topilmadi.\nQayta urinib ko'ring:"
        )
        return

    if len(oqituvchilar) == 1:
        await state.clear()
        o = await get_oqituvchi(pool, oqituvchilar[0]["id"])
        darslar = await get_oqituvchi_bugungi_dars(pool, o["id"])
        matn = format_oqituvchi_karta(o, darslar)
        await message.answer(
            matn,
            reply_markup=oqituvchi_nav_kb(o.get("kafedra_id", 0), o.get("telegram_file_id")),
            parse_mode="HTML"
        )
    else:
        await state.set_state(Qidiruv.natija_tanlash)
        await state.update_data(qidiruv_natijalar=[o["id"] for o in oqituvchilar])
        await message.answer(
            f"🔍 <b>{query}</b> bo'yicha {len(oqituvchilar)} ta natija topildi.\nBirini tanlang:",
            reply_markup=qidiruv_natijalari_kb(oqituvchilar)
        )
