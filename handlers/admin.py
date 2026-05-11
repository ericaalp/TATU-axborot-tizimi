import re
from collections import defaultdict
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

from config import SUPERADMIN_IDS
from db import (
    get_all_kafedralar, get_kafedralar_by_bino, get_kafedra,
    get_kafedra_oqituvchilari, get_oqituvchi, get_oqituvchi_by_search,
    get_oqituvchi_jadval, create_oqituvchi, update_oqituvchi, delete_oqituvchi,
    create_dars, create_xona, set_xona_holat,
    get_qavat_xonalari, get_xona_tafsilot, get_xona_bugungi_jadval,
    get_xona_kun_jadvali, get_xona_haftalik_jadval, get_all_stats, send_broadcast,
    get_haftalik_hisobot, get_all_foydalanuvchilar,
    JUFT_VAQTLAR, bugungi_kun, hozirgi_juft,
)
from states import (
    AdminOqituvchi, AdminJadval,
    AdminXonaMenu, AdminXonaQosh, AdminXonaBand, AdminXonaJadval,
    AdminTahrir, AdminXabar,
)


# ─── Constants ────────────────────────────────────────────────────────────────

JUFTLIKLAR = {
    1: ("08:30", "09:50"),
    2: ("10:00", "11:20"),
    3: ("11:30", "12:50"),
    4: ("13:30", "14:50"),
    5: ("15:00", "16:20"),
    6: ("16:30", "17:50"),
}

KUN_TARTIBI = ["dushanba", "seshanba", "chorshanba", "payshanba", "juma"]
KUN_NOMI = {
    "dushanba": "Dushanba", "seshanba": "Seshanba",
    "chorshanba": "Chorshanba", "payshanba": "Payshanba", "juma": "Juma",
}

FAKULTETLAR = {
    "A": "Telekommunikatsiya va kiberxavfsizlik",
    "B": "Kompyuter injiniringi va sun'iy intellekt",
}

TAHRIR_MAYDON_NOMI = {
    "ism": "Ism",
    "tel_raqam": "Telefon (+998XXXXXXXXX yoki —)",
    "telegram_username": "Telegram username (@ belgisisiz yoki —)",
    "kafedra_id": "Kafedra",
    "xona_raqam": "Xona raqami",
    "telegram_file_id": "Rasm",
}


# ─── Filter ───────────────────────────────────────────────────────────────────

class RoleFilter(Filter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, event) -> bool:
        user = getattr(event, "from_user", None)
        user_id = user.id if user else 0
        if self.role == "superadmin":
            return user_id in SUPERADMIN_IDS
        return False


router = Router()
router.message.filter(RoleFilter("superadmin"))
router.callback_query.filter(RoleFilter("superadmin"))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _tel_valid(tel: str) -> bool:
    return bool(re.match(r'^\+998\d{9}$', tel))


def format_oqituvchi_karta(o: dict) -> str:
    tel = o.get("tel_raqam") or "—"
    tg = f"@{o['telegram_username']}" if o.get("telegram_username") else "—"
    kafedra = o.get("kafedra_nomi") or "—"
    xona = f"{o['xona_raqam']}-xona" if o.get("xona_raqam") else "—"
    return (
        f"👤 <b>{o['familiya']} {o['ism']}</b>\n"
        f"🏫 {kafedra}, {xona}\n"
        f"📞 {tel}\n"
        f"✈️ {tg}"
    )


def format_haftalik_jadval(darslar: list[dict]) -> str:
    if not darslar:
        return "\n\n📅 Dars jadvali hali kiritilmagan."
    by_kun: dict[str, list] = defaultdict(list)
    for d in darslar:
        by_kun[d["kun"]].append(d)
    matn = "\n\n📅 <b>Haftalik dars jadvali:</b>"
    for kun in KUN_TARTIBI:
        if kun not in by_kun:
            continue
        matn += f"\n\n<b>{KUN_NOMI[kun]}:</b>"
        for d in sorted(by_kun[kun], key=lambda x: x["boshlanish"]):
            bosh = str(d["boshlanish"])[:5]
            tug = str(d["tugash"])[:5]
            guruh = d.get("guruh") or "—"
            matn += f"\n⏰ {bosh}–{tug} → {d['xona_raqam']}-xona, {d['bino']}-bino"
            matn += f"\n{d['fan_nomi']} — {guruh}"
    return matn


# ─── Keyboards ────────────────────────────────────────────────────────────────

def admin_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ O'qituvchi qo'shish"), KeyboardButton(text="🏠 Xona boshqaruv")],
            [KeyboardButton(text="🏛 Kafedralar")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📢 Ommaviy xabar")],
        ],
        resize_keyboard=True,
        persistent=True,
    )


def _rm() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def _kb(rows: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in row]
        for row in rows
    ])


def oqituvchi_amal_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("👤 O'qituvchi ma'lumotlarini qo'shish", "admin_oq_qosh")],
        [("📅 Dars jadvali qo'shish", "admin_jadval_qosh")],
    ])


def admin_xona_bino_kb() -> InlineKeyboardMarkup:
    return _kb([[("🏢 A-bino", "admin_xona_bino:A"), ("🏢 B-bino", "admin_xona_bino:B")]])


def admin_xona_menu_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("➕ Xona qo'shish", "admin_xona_qosh")],
        [("🔒 Xona bandligi", "admin_xona_band")],
        [("📅 Haftalik jadval", "admin_xona_jadval")],
        [("◀️ Bino tanlash", "admin_xona_bino_menu")],
    ])


def admin_xona_qavat_kb(bino: str) -> InlineKeyboardMarkup:
    return _kb([[
        ("1-qavat", f"admin_xqavat:1:{bino}"),
        ("2-qavat", f"admin_xqavat:2:{bino}"),
        ("3-qavat", f"admin_xqavat:3:{bino}"),
    ]])


def admin_xona_rooms_kb(xonalar: list[dict], bino: str, back: str) -> InlineKeyboardMarkup:
    rows = []
    qator = []
    for x in xonalar:
        belgi = "🔴" if x['holat'] == 'band' else "✅"
        qator.append((f"{belgi}{x['raqam']}", f"admin_xona_sel:{x['raqam']}:{bino}"))
        if len(qator) == 4:
            rows.append(qator)
            qator = []
    if qator:
        rows.append(qator)
    rows.append([("◀️ Orqaga", back)])
    return _kb(rows)


def admin_xb_options_kb(raqam: int, bino: str, qavat: int) -> InlineKeyboardMarkup:
    return _kb([
        [("🔴 Band qilish", f"admin_xb_band_start:{raqam}:{bino}")],
        [("✅ Bo'sh qilish", f"admin_xb_bosh:{raqam}:{bino}")],
        [("◀️ Xonalarga qaytish", f"admin_xona_band_r:{qavat}:{bino}")],
    ])


def admin_xb_kun_kb(raqam: int, bino: str) -> InlineKeyboardMarkup:
    kunlar = [
        ("Du", "dushanba"), ("Se", "seshanba"), ("Ch", "chorshanba"),
        ("Pa", "payshanba"), ("Ju", "juma"),
    ]
    return _kb([
        [(nom, f"admin_xb_kun:{kun}") for nom, kun in kunlar],
        [("◀️ Orqaga", f"admin_xb_xona_orqa:{raqam}:{bino}")],
    ])


def admin_xb_juft_kb() -> InlineKeyboardMarkup:
    rows = []
    qator = []
    for n, (bosh, _) in JUFT_VAQTLAR.items():
        qator.append((f"{n}-juft {bosh}", f"admin_xb_juft:{n}"))
        if len(qator) == 3:
            rows.append(qator)
            qator = []
    if qator:
        rows.append(qator)
    rows.append([("◀️ Kun tanlashga qaytish", "admin_xb_kun_orqa")])
    return _kb(rows)


def admin_xb_tasdiq_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("✅ Tasdiqlash", "admin_xb_ha"), ("✏️ Tahrirlash", "admin_xb_tahrir")],
    ])


def fakultet_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("🏢 A-bino: Telekommunikatsiya va kiberxavfsizlik", "admin_fak:A")],
        [("🏢 B-bino: Kompyuter injiniringi va sun'iy intellekt", "admin_fak:B")],
    ])


def kafedralar_kb(kafedralar: list[dict]) -> InlineKeyboardMarkup:
    rows = [[(k["nomi"], f"admin_kaf_kor:{k['id']}")] for k in kafedralar]
    rows.append([("◀️ Fakultetlar", "admin_fak_orqa")])
    return _kb(rows)


def oqituvchilar_kb(oqituvchilar: list[dict], kafedra_id: int, bino: str) -> InlineKeyboardMarkup:
    rows = []
    for o in oqituvchilar:
        ism_q = (o["ism"][0] + ".") if o.get("ism") else ""
        rows.append([(f"{o['familiya']} {ism_q}", f"admin_oq_kor:{o['id']}:{kafedra_id}")])
    rows.append([("◀️ Kafedralar", f"admin_fak:{bino}")])
    return _kb(rows)


def oqituvchi_nav_kb(oqituvchi_id: int, kafedra_id: int) -> InlineKeyboardMarkup:
    return _kb([
        [
            ("✏️ Tahrirlash", f"admin_tahrir:{oqituvchi_id}:{kafedra_id}"),
            ("🗑 O'chirish", f"admin_ochir:{oqituvchi_id}:{kafedra_id}"),
        ],
        [("◀️ Orqaga", f"admin_oq_orqa:{kafedra_id}")],
    ])


def tahrir_maydon_kb(oqituvchi_id: int) -> InlineKeyboardMarkup:
    return _kb([
        [
            ("Ism", f"admin_maydon:ism:{oqituvchi_id}"),
            ("Telefon", f"admin_maydon:tel_raqam:{oqituvchi_id}"),
        ],
        [
            ("Telegram", f"admin_maydon:telegram_username:{oqituvchi_id}"),
            ("Kafedra", f"admin_maydon:kafedra_id:{oqituvchi_id}"),
        ],
        [
            ("Xona", f"admin_maydon:xona_raqam:{oqituvchi_id}"),
            ("Rasm", f"admin_maydon:telegram_file_id:{oqituvchi_id}"),
        ],
    ])


def ochirish_tasdiq_kb(oqituvchi_id: int, kafedra_id: int) -> InlineKeyboardMarkup:
    return _kb([
        [
            ("✅ Ha, o'chirish", f"admin_ochir_ha:{oqituvchi_id}:{kafedra_id}"),
            ("❌ Bekor", f"admin_ochir_yoq:{oqituvchi_id}:{kafedra_id}"),
        ]
    ])


def admin_kafedra_tanlash_kb(kafedralar: list[dict]) -> InlineKeyboardMarkup:
    rows = [[(k["nomi"], f"admin_kaf:{k['id']}")] for k in kafedralar]
    return _kb(rows)


def admin_tahrir_kafedra_kb(kafedralar: list[dict], oqituvchi_id: int) -> InlineKeyboardMarkup:
    rows = [[(k["nomi"], f"admin_tahrir_kaf:{k['id']}:{oqituvchi_id}")] for k in kafedralar]
    return _kb(rows)


def bino_kb(prefix: str = "admin_bino") -> InlineKeyboardMarkup:
    return _kb([[("A-bino", f"{prefix}:A"), ("B-bino", f"{prefix}:B")]])


def kun_tanlash_kb() -> InlineKeyboardMarkup:
    kunlar = [("Du", "dushanba"), ("Se", "seshanba"), ("Ch", "chorshanba"), ("Pa", "payshanba"), ("Ju", "juma")]
    return _kb([[("Du", "admin_kun:dushanba"), ("Se", "admin_kun:seshanba"), ("Ch", "admin_kun:chorshanba"),
                 ("Pa", "admin_kun:payshanba"), ("Ju", "admin_kun:juma")]])


def juft_tanlash_kb() -> InlineKeyboardMarkup:
    rows = [[(f"{n}-juft {bosh}-{tug}", f"admin_juft:{n}")] for n, (bosh, tug) in JUFTLIKLAR.items()]
    return _kb(rows)


def holat_tanlash_kb() -> InlineKeyboardMarkup:
    return _kb([[("🔴 Band", "admin_holat:band"), ("✅ Bo'sh", "admin_holat:bosh")]])


def statistika_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("📅 Haftalik hisobot", "admin_stat_hafta"), ("👥 Foydalanuvchilar ro'yxati", "admin_stat_users")],
    ])


def broadcast_tasdiq_kb() -> InlineKeyboardMarkup:
    return _kb([[("✅ Yuborish", "admin_broadcast_ha"), ("❌ Bekor", "admin_broadcast_yoq")]])


def qidiruv_kb(oqituvchilar: list[dict], prefix: str) -> InlineKeyboardMarkup:
    rows = []
    for o in oqituvchilar:
        ism_q = (o["ism"][0] + ".") if o.get("ism") else ""
        rows.append([(f"{o['familiya']} {ism_q}", f"{prefix}:{o['id']}")])
    return _kb(rows)


# ─── /cancel ──────────────────────────────────────────────────────────────────

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu_kb())


# ─── 1. O'QITUVCHI QO'SHISH ──────────────────────────────────────────────────

@router.message(F.text == "➕ O'qituvchi qo'shish")
async def oqituvchi_qoshish_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amalni tanlang:", reply_markup=oqituvchi_amal_kb())


# ── 1a. O'qituvchi ma'lumotlari ──────────────────────────────────────────────

@router.callback_query(F.data == "admin_oq_qosh")
async def oq_qosh_boshlash(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Ism-familiyasini kiriting:\n<i>Misol: Karimov Jasur</i>")
    await state.set_state(AdminOqituvchi.ism_familiya)
    await call.answer()


@router.message(AdminOqituvchi.ism_familiya)
async def oq_ism_familiya(message: Message, state: FSMContext, pool):
    qismlar = message.text.strip().split(maxsplit=1)
    if len(qismlar) < 2:
        await message.answer("❌ Familiya va ismni bo'sh joy bilan ajratib kiriting:")
        return
    familiya, ism = qismlar[0], qismlar[1]
    await state.update_data(familiya=familiya, ism=ism)
    kafedralar = await get_all_kafedralar(pool)
    await message.answer("📌 Kafedrani tanlang:", reply_markup=admin_kafedra_tanlash_kb(kafedralar))
    await state.set_state(AdminOqituvchi.kafedra)


@router.callback_query(AdminOqituvchi.kafedra, F.data.startswith("admin_kaf:"))
async def oq_kafedra(call: CallbackQuery, state: FSMContext):
    kafedra_id = int(call.data.split(":")[1])
    await state.update_data(kafedra_id=kafedra_id)
    await call.message.edit_text("📞 Telefon (+998XXXXXXXXX), yo'q bo'lsa — yozing:")
    await state.set_state(AdminOqituvchi.tel)
    await call.answer()


@router.message(AdminOqituvchi.tel)
async def oq_tel(message: Message, state: FSMContext):
    tel = message.text.strip()
    if tel != "—" and not _tel_valid(tel):
        await message.answer("❌ Format: +998XXXXXXXXX yoki — (tire):")
        return
    await state.update_data(tel_raqam=None if tel == "—" else tel)
    await message.answer("✈️ Telegram username (@ belgisisiz), yo'q bo'lsa — yozing:")
    await state.set_state(AdminOqituvchi.telegram)


@router.message(AdminOqituvchi.telegram)
async def oq_telegram(message: Message, state: FSMContext):
    val = message.text.strip()
    username = None if val == "—" else val.lstrip("@")
    await state.update_data(telegram_username=username)
    await message.answer("🏠 Kafedra xona raqami:")
    await state.set_state(AdminOqituvchi.xona_raqam)


@router.message(AdminOqituvchi.xona_raqam)
async def oq_xona_raqam(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam kiriting:")
        return
    await state.update_data(xona_raqam=int(message.text.strip()))
    await message.answer("🏢 Binoni tanlang:", reply_markup=bino_kb("admin_bino"))
    await state.set_state(AdminOqituvchi.bino)


@router.callback_query(AdminOqituvchi.bino, F.data.startswith("admin_bino:"))
async def oq_bino(call: CallbackQuery, state: FSMContext, pool):
    bino = call.data.split(":")[1]
    data = await state.get_data()
    oqituvchi_id = await create_oqituvchi(
        pool,
        kafedra_id=data["kafedra_id"],
        ism=data["ism"],
        familiya=data["familiya"],
        otasining_ismi=None,
        tel_raqam=data.get("tel_raqam"),
        telegram_username=data.get("telegram_username"),
        xona_raqam=data["xona_raqam"],
        bino=bino,
    )
    await state.clear()
    if oqituvchi_id:
        await call.message.edit_text(f"✅ {data['ism']} muvaffaqiyatli qo'shildi!")
    else:
        await call.message.edit_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
    await call.message.answer("Admin panel:", reply_markup=admin_menu_kb())
    await call.answer()


# ── 1b. Dars jadvali qo'shish ────────────────────────────────────────────────

@router.callback_query(F.data == "admin_jadval_qosh")
async def jadval_qosh_boshlash(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🔍 O'qituvchi ismini kiriting:")
    await state.set_state(AdminJadval.oqituvchi_qidirish)
    await call.answer()


@router.message(AdminJadval.oqituvchi_qidirish)
async def jadval_oqituvchi_qidirish(message: Message, state: FSMContext, pool):
    natijalar = await get_oqituvchi_by_search(pool, message.text.strip())
    if not natijalar:
        await message.answer("❌ Topilmadi. Qayta kiriting:")
        return
    if len(natijalar) == 1:
        o = natijalar[0]
        await state.update_data(oqituvchi_id=o["id"])
        await message.answer(
            f"👤 <b>{o['familiya']} {o['ism']}</b>\n\nKunni tanlang:",
            reply_markup=kun_tanlash_kb(),
        )
        await state.set_state(AdminJadval.kun)
    else:
        await message.answer("Birini tanlang:", reply_markup=qidiruv_kb(natijalar, "jadval_oq"))
        await state.set_state(AdminJadval.oqituvchi_tanlash)


@router.callback_query(AdminJadval.oqituvchi_tanlash, F.data.startswith("jadval_oq:"))
async def jadval_oqituvchi_tanlash(call: CallbackQuery, state: FSMContext, pool):
    oqituvchi_id = int(call.data.split(":")[1])
    o = await get_oqituvchi(pool, oqituvchi_id)
    await state.update_data(oqituvchi_id=oqituvchi_id)
    await call.message.edit_text(
        f"👤 <b>{o['familiya']} {o['ism']}</b>\n\nKunni tanlang:",
        reply_markup=kun_tanlash_kb(),
    )
    await state.set_state(AdminJadval.kun)
    await call.answer()


@router.callback_query(AdminJadval.kun, F.data.startswith("admin_kun:"))
async def jadval_kun(call: CallbackQuery, state: FSMContext):
    kun = call.data.split(":")[1]
    await state.update_data(kun=kun)
    await call.message.edit_text(
        f"✅ Kun: <b>{KUN_NOMI[kun]}</b>\n\nJuftlikni tanlang:",
        reply_markup=juft_tanlash_kb(),
    )
    await state.set_state(AdminJadval.juft)
    await call.answer()


@router.callback_query(AdminJadval.juft, F.data.startswith("admin_juft:"))
async def jadval_juft(call: CallbackQuery, state: FSMContext):
    n = int(call.data.split(":")[1])
    boshlanish, tugash = JUFTLIKLAR[n]
    await state.update_data(juft_raqam=n, boshlanish=boshlanish, tugash=tugash)
    await call.message.edit_text("🏠 Xona raqamini kiriting:")
    await state.set_state(AdminJadval.xona)
    await call.answer()


@router.message(AdminJadval.xona)
async def jadval_xona(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam kiriting:")
        return
    await state.update_data(xona_raqam=int(message.text.strip()))
    await message.answer("🏢 Binoni tanlang:", reply_markup=bino_kb("admin_bino"))
    await state.set_state(AdminJadval.bino)


@router.callback_query(AdminJadval.bino, F.data.startswith("admin_bino:"))
async def jadval_bino(call: CallbackQuery, state: FSMContext):
    bino = call.data.split(":")[1]
    await state.update_data(bino=bino)
    await call.message.edit_text("📖 Fan nomini kiriting:")
    await state.set_state(AdminJadval.fan)
    await call.answer()


@router.message(AdminJadval.fan)
async def jadval_fan(message: Message, state: FSMContext):
    await state.update_data(fan_nomi=message.text.strip())
    await message.answer("👥 Guruh (masalan: AKT-23-01), yo'q bo'lsa — yozing:")
    await state.set_state(AdminJadval.guruh)


@router.message(AdminJadval.guruh)
async def jadval_guruh(message: Message, state: FSMContext, pool):
    guruh_val = message.text.strip()
    guruh = None if guruh_val == "—" else guruh_val
    data = await state.get_data()
    ok = await create_dars(
        pool,
        oqituvchi_id=data["oqituvchi_id"],
        kun=data["kun"],
        boshlanish=data["boshlanish"],
        tugash=data["tugash"],
        xona_raqam=data["xona_raqam"],
        bino=data["bino"],
        fan_nomi=data["fan_nomi"],
        guruh=guruh,
    )
    await state.clear()
    if not ok:
        await message.answer("❌ Dars qo'shishda xato yuz berdi!", reply_markup=admin_menu_kb())
        return

    band_hozir = False
    bugun = bugungi_kun()
    if bugun == data["kun"]:
        hozir = datetime.now().strftime('%H:%M')
        if data["boshlanish"] <= hozir <= data["tugash"]:
            await set_xona_holat(pool, data["xona_raqam"], data["bino"], band=True)
            band_hozir = True

    matn = (
        f"✅ Dars muvaffaqiyatli qo'shildi!\n"
        f"{KUN_NOMI.get(data['kun'], data['kun'])} "
        f"{data['boshlanish']}–{data['tugash']}\n"
        f"{data['xona_raqam']}-xona, {data['bino']}-bino\n"
        f"{data['fan_nomi']} — {guruh or '—'}"
    )
    if band_hozir:
        matn += "\n\n🔴 Xona hozir band deb belgilandi."
    await message.answer(matn, reply_markup=admin_menu_kb())


# ─── 2. XONA BOSHQARUV ────────────────────────────────────────────────────────

_BINO_NOMI = {
    "A": "Telekommunikatsiya va kiberxavfsizlik",
    "B": "Kompyuter injiniringi va sun'iy intellekt",
}
_KUN_NOMI_UZ = {
    'dushanba': 'Dushanba', 'seshanba': 'Seshanba', 'chorshanba': 'Chorshanba',
    'payshanba': 'Payshanba', 'juma': 'Juma',
}


def _format_xona_bugungi(raqam: int, bino: str, xona: dict | None, darslar: list[dict]) -> str:
    manual_holat = "🔴 Band" if (xona and xona.get('band')) else "✅ Bo'sh"
    band_gacha_str = f" ({xona['band_gacha']}gacha)" if (xona and xona.get('band_gacha')) else ""
    matn = f"🏠 <b>{bino}-bino, {raqam}-xona</b>\nQo'lda belgilangan: {manual_holat}{band_gacha_str}\n"
    matn += "\n📅 <b>Bugungi dars jadvali:</b>"
    hozirgi = hozirgi_juft()
    dars_by_juft = {d['juft_raqami']: d for d in darslar if d.get('juft_raqami')}
    for j_n, (bosh, tug) in JUFT_VAQTLAR.items():
        d = dars_by_juft.get(j_n)
        hozir_belgisi = " ◀" if hozirgi == j_n else ""
        if d:
            oq = f"{d['familiya']} {d['ism']}".strip()
            guruh = d.get('guruh') or '—'
            matn += f"\n{j_n}-juft {bosh}–{tug}{hozir_belgisi} 🔴"
            matn += f"\n  {oq} — {d['fan_nomi']}, {guruh}"
        else:
            matn += f"\n{j_n}-juft {bosh}–{tug}{hozir_belgisi} ✅ BO'SH"
    return matn


@router.message(F.text == "🏠 Xona boshqaruv")
async def xona_boshqaruv_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏢 Binoni tanlang:", reply_markup=admin_xona_bino_kb())


@router.callback_query(F.data == "admin_xona_bino_menu")
async def xona_bino_menu_orqa(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🏢 Binoni tanlang:", reply_markup=admin_xona_bino_kb())
    await call.answer()


@router.callback_query(F.data.startswith("admin_xona_bino:"))
async def xona_bino_tanlash(call: CallbackQuery, state: FSMContext):
    bino = call.data.split(":")[1]
    await state.update_data(bino=bino)
    await state.set_state(AdminXonaMenu.amal)
    fname = _BINO_NOMI.get(bino, bino)
    await call.message.edit_text(
        f"🏢 <b>{bino}-bino</b> — {fname}\n\nAmalni tanlang:",
        reply_markup=admin_xona_menu_kb(),
    )
    await call.answer()


# ── 2a. Xona qo'shish ────────────────────────────────────────────────────────

@router.callback_query(AdminXonaMenu.amal, F.data == "admin_xona_qosh")
async def xona_qosh_boshlash(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bino = data.get('bino', 'A')
    await call.message.edit_text(
        f"🏢 {bino}-bino — Qavatni tanlang:",
        reply_markup=admin_xona_qavat_kb(bino),
    )
    await state.set_state(AdminXonaQosh.qavat)
    await call.answer()


@router.callback_query(AdminXonaQosh.qavat, F.data.startswith("admin_xqavat:"))
async def xona_qosh_qavat_sel(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    qavat = int(parts[1])
    bino = parts[2]
    await state.update_data(qavat=qavat, bino=bino)
    await call.message.edit_text(
        f"🏢 {bino}-bino, {qavat}-qavat\n\nXona raqamini kiriting:",
    )
    await state.set_state(AdminXonaQosh.raqam)
    await call.answer()


@router.message(AdminXonaQosh.raqam)
async def xona_qosh_raqam_kiritish(message: Message, state: FSMContext, pool):
    if not message.text.strip().isdigit():
        await message.answer("❌ Faqat raqam kiriting:")
        return
    raqam = int(message.text.strip())
    data = await state.get_data()
    await create_xona(pool, raqam=raqam, bino=data['bino'], qavat=data['qavat'])
    await state.clear()
    await message.answer(
        f"✅ {data['bino']}-bino, {data['qavat']}-qavat, {raqam}-xona qo'shildi.",
        reply_markup=admin_menu_kb(),
    )


# ── 2b. Xona bandligi ────────────────────────────────────────────────────────

_KUN_NOMI_BAND = {
    'dushanba': 'Dushanba', 'seshanba': 'Seshanba', 'chorshanba': 'Chorshanba',
    'payshanba': 'Payshanba', 'juma': 'Juma',
}


@router.callback_query(AdminXonaMenu.amal, F.data == "admin_xona_band")
async def xona_band_boshlash(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bino = data.get('bino', 'A')
    await call.message.edit_text(
        f"🏢 {bino}-bino — Qavatni tanlang:",
        reply_markup=admin_xona_qavat_kb(bino),
    )
    await state.set_state(AdminXonaBand.qavat)
    await call.answer()


@router.callback_query(AdminXonaBand.qavat, F.data.startswith("admin_xqavat:"))
async def xona_band_qavat_sel(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    qavat = int(parts[1])
    bino = parts[2]
    await state.update_data(qavat=qavat, bino=bino)
    xonalar = await get_qavat_xonalari(pool, bino, qavat)
    if not xonalar:
        await call.message.edit_text(
            f"❌ {bino}-bino {qavat}-qavatda xonalar topilmadi.",
            reply_markup=_kb([[("◀️ Orqaga", f"admin_xona_bino:{bino}")]]),
        )
        await call.answer()
        return
    await call.message.edit_text(
        f"🏢 <b>{bino}-bino, {qavat}-qavat</b>\n✅ bo'sh  🔴 band\n\nXonani tanlang:",
        reply_markup=admin_xona_rooms_kb(xonalar, bino, f"admin_xona_bino:{bino}"),
    )
    await state.set_state(AdminXonaBand.xona)
    await call.answer()


@router.callback_query(AdminXonaBand.xona, F.data.startswith("admin_xona_sel:"))
async def xona_band_xona_sel(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    raqam = int(parts[1])
    bino = parts[2]
    data = await state.get_data()
    qavat = data.get('qavat', 1)
    await state.update_data(raqam=raqam, bino=bino)
    xona = await get_xona_tafsilot(pool, raqam, bino)
    holat = "🔴 Band" if (xona and xona.get('band')) else "✅ Bo'sh"
    band_str = f"\n⏰ Band vaqti: {xona['band_gacha']}" if (xona and xona.get('band_gacha')) else ""
    matn = (
        f"🏠 <b>{bino}-bino, {raqam}-xona</b>\n"
        f"Joriy holat: {holat}{band_str}\n\n"
        f"Amalni tanlang:"
    )
    await call.message.edit_text(matn, reply_markup=admin_xb_options_kb(raqam, bino, qavat))
    await call.answer()


@router.callback_query(AdminXonaBand.xona, F.data.startswith("admin_xb_bosh:"))
async def xona_bosh_qilish(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    raqam = int(parts[1])
    bino = parts[2]
    await set_xona_holat(pool, raqam, bino, band=False, band_gacha=None)
    await state.clear()
    await call.message.edit_text(f"✅ {bino}-bino, {raqam}-xona bo'sh qilindi.")
    await call.message.answer("Admin panel:", reply_markup=admin_menu_kb())
    await call.answer()


@router.callback_query(AdminXonaBand.xona, F.data.startswith("admin_xb_band_start:"))
async def xona_band_kun_boshlash(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    raqam = int(parts[1])
    bino = parts[2]
    await state.update_data(raqam=raqam, bino=bino)
    await call.message.edit_text(
        f"🏠 <b>{bino}-bino, {raqam}-xona</b>\n\n📅 Hafta kunini tanlang:",
        reply_markup=admin_xb_kun_kb(raqam, bino),
    )
    await state.set_state(AdminXonaBand.kun)
    await call.answer()


@router.callback_query(AdminXonaBand.xona, F.data.startswith("admin_xona_band_r:"))
async def xona_band_rooms_orqa(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    qavat = int(parts[1])
    bino = parts[2]
    await state.update_data(qavat=qavat, bino=bino)
    xonalar = await get_qavat_xonalari(pool, bino, qavat)
    await call.message.edit_text(
        f"🏢 <b>{bino}-bino, {qavat}-qavat</b>\n✅ bo'sh  🔴 band\n\nXonani tanlang:",
        reply_markup=admin_xona_rooms_kb(xonalar, bino, f"admin_xona_bino:{bino}"),
    )
    await call.answer()


@router.callback_query(AdminXonaBand.kun, F.data.startswith("admin_xb_kun:"))
async def xona_band_kun_sel(call: CallbackQuery, state: FSMContext, pool):
    kun = call.data.split(":")[1]
    await state.update_data(kun=kun)
    data = await state.get_data()
    raqam = data['raqam']
    bino = data['bino']
    darslar = await get_xona_kun_jadvali(pool, raqam, bino, kun)
    dars_by_juft = {d['juft_raqami']: d for d in darslar if d.get('juft_raqami')}
    kun_nomi = _KUN_NOMI_BAND.get(kun, kun)
    matn = f"🏠 <b>{bino}-bino, {raqam}-xona</b>\n📅 {kun_nomi} — dars jadvali:\n"
    for j_n, (bosh, tug) in JUFT_VAQTLAR.items():
        d = dars_by_juft.get(j_n)
        matn += f"\n{j_n}-juft {bosh}–{tug}: "
        if d:
            oq = f"{d['familiya']} {d['ism'][:1]}."
            guruh = d.get('guruh') or '—'
            matn += f"{oq} | {d['fan_nomi']} | {guruh}"
        else:
            matn += "BO'SH"
    matn += "\n\nBand qilish uchun juftlikni tanlang:"
    await call.message.edit_text(matn, reply_markup=admin_xb_juft_kb())
    await state.set_state(AdminXonaBand.juft)
    await call.answer()


@router.callback_query(AdminXonaBand.kun, F.data.startswith("admin_xb_xona_orqa:"))
async def xona_band_kun_xona_orqa(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    raqam = int(parts[1])
    bino = parts[2]
    data = await state.get_data()
    qavat = data.get('qavat', 1)
    xona = await get_xona_tafsilot(pool, raqam, bino)
    holat = "🔴 Band" if (xona and xona.get('band')) else "✅ Bo'sh"
    band_str = f"\n⏰ Band vaqti: {xona['band_gacha']}" if (xona and xona.get('band_gacha')) else ""
    matn = (
        f"🏠 <b>{bino}-bino, {raqam}-xona</b>\n"
        f"Joriy holat: {holat}{band_str}\n\nAmalni tanlang:"
    )
    await call.message.edit_text(matn, reply_markup=admin_xb_options_kb(raqam, bino, qavat))
    await state.set_state(AdminXonaBand.xona)
    await call.answer()


@router.callback_query(AdminXonaBand.juft, F.data.startswith("admin_xb_juft:"))
async def xona_band_juft_sel(call: CallbackQuery, state: FSMContext, pool):
    juft_n = int(call.data.split(":")[1])
    bosh, tug = JUFT_VAQTLAR[juft_n]
    await state.update_data(juft_raqami=juft_n, boshlanish=bosh, tugash=tug)
    data = await state.get_data()
    raqam = data['raqam']
    bino = data['bino']
    kun = data['kun']
    kun_nomi = _KUN_NOMI_BAND.get(kun, kun)
    darslar = await get_xona_kun_jadvali(pool, raqam, bino, kun)
    dars_by_juft = {d['juft_raqami']: d for d in darslar if d.get('juft_raqami')}
    d = dars_by_juft.get(juft_n)
    matn = (
        f"📋 <b>Tasdiqlash</b>\n\n"
        f"🏠 {bino}-bino, {raqam}-xona\n"
        f"📅 Kun: {kun_nomi}\n"
        f"⏰ {juft_n}-juft ({bosh}–{tug})\n\n"
        f"<b>Bu juftlikda:</b>\n"
    )
    if d:
        oq = f"{d['familiya']} {d['ism']}"
        guruh = d.get('guruh') or '—'
        matn += f"👤 {oq}\n📖 {d['fan_nomi']}\n👥 {guruh} guruhi\n"
    else:
        matn += "✅ BO'SH (jadvalda dars yo'q)\n"
    matn += f"\n⚠️ Xona <b>{tug}</b> gacha band bo'ladi.\nTasdiqlaysizmi?"
    await call.message.edit_text(matn, reply_markup=admin_xb_tasdiq_kb())
    await state.set_state(AdminXonaBand.tasdiq)
    await call.answer()


@router.callback_query(AdminXonaBand.juft, F.data == "admin_xb_kun_orqa")
async def xona_band_juft_kun_orqa(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    raqam = data['raqam']
    bino = data['bino']
    await call.message.edit_text(
        f"🏠 <b>{bino}-bino, {raqam}-xona</b>\n\n📅 Hafta kunini tanlang:",
        reply_markup=admin_xb_kun_kb(raqam, bino),
    )
    await state.set_state(AdminXonaBand.kun)
    await call.answer()


@router.callback_query(AdminXonaBand.tasdiq, F.data == "admin_xb_ha")
async def xona_band_tasdiq(call: CallbackQuery, state: FSMContext, pool):
    data = await state.get_data()
    await set_xona_holat(pool, data['raqam'], data['bino'], band=True, band_gacha=data['tugash'])
    await state.clear()
    await call.message.edit_text(
        f"✅ {data['bino']}-bino, {data['raqam']}-xona — "
        f"{data['kun'].capitalize()}, {data['juft_raqami']}-juft {data['tugash']} gacha band qilindi."
    )
    await call.message.answer("Admin panel:", reply_markup=admin_menu_kb())
    await call.answer()


@router.callback_query(AdminXonaBand.tasdiq, F.data == "admin_xb_tahrir")
async def xona_band_tahrir(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    raqam = data['raqam']
    bino = data['bino']
    await call.message.edit_text(
        f"🏠 <b>{bino}-bino, {raqam}-xona</b>\n\n📅 Hafta kunini tanlang:",
        reply_markup=admin_xb_kun_kb(raqam, bino),
    )
    await state.set_state(AdminXonaBand.kun)
    await call.answer()


# ── 2c. Haftalik jadval ────────────────────────────────────────────────────────

@router.callback_query(AdminXonaMenu.amal, F.data == "admin_xona_jadval")
async def xona_jadval_boshlash(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bino = data.get('bino', 'A')
    await call.message.edit_text(
        f"🏢 {bino}-bino — Qavatni tanlang:",
        reply_markup=admin_xona_qavat_kb(bino),
    )
    await state.set_state(AdminXonaJadval.qavat)
    await call.answer()


@router.callback_query(AdminXonaJadval.qavat, F.data.startswith("admin_xqavat:"))
async def xona_jadval_qavat_sel(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    qavat = int(parts[1])
    bino = parts[2]
    await state.update_data(qavat=qavat, bino=bino)
    xonalar = await get_qavat_xonalari(pool, bino, qavat)
    if not xonalar:
        await call.message.edit_text(
            f"❌ {bino}-bino {qavat}-qavatda xonalar topilmadi.",
            reply_markup=_kb([[("◀️ Orqaga", f"admin_xona_bino:{bino}")]]),
        )
        await call.answer()
        return
    await call.message.edit_text(
        f"🏢 <b>{bino}-bino, {qavat}-qavat</b>\nHaftalik jadval uchun xonani tanlang:",
        reply_markup=admin_xona_rooms_kb(xonalar, bino, f"admin_xona_bino:{bino}"),
    )
    await state.set_state(AdminXonaJadval.xona)
    await call.answer()


@router.callback_query(AdminXonaJadval.xona, F.data.startswith("admin_xona_sel:"))
async def xona_jadval_xona_sel(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    raqam = int(parts[1])
    bino = parts[2]
    data = await state.get_data()
    qavat = data.get('qavat', 1)
    haftalik = await get_xona_haftalik_jadval(pool, raqam, bino)
    matn = f"📅 <b>{bino}-bino, {raqam}-xona — Haftalik jadval:</b>"
    for kun in ['dushanba', 'seshanba', 'chorshanba', 'payshanba', 'juma']:
        darslar = haftalik.get(kun, [])
        matn += f"\n\n<b>{_KUN_NOMI_UZ[kun]}:</b>"
        if darslar:
            for d in darslar:
                bosh = str(d['boshlanish'])[:5]
                tug = str(d['tugash'])[:5]
                oq = f"{d['familiya']} {d['ism']}".strip()
                j = d.get('juft_raqami', '?')
                guruh = d.get('guruh') or '—'
                matn += f"\n{j}-juft {bosh}–{tug} — {oq}"
                matn += f"\n{d['fan_nomi']} | {guruh}"
        else:
            matn += " Bo'sh"
    await call.message.edit_text(
        matn,
        reply_markup=_kb([[("◀️ Xonalarga qaytish", f"admin_xona_jadval_r:{qavat}:{bino}")]]),
    )
    await call.answer()


@router.callback_query(AdminXonaJadval.xona, F.data.startswith("admin_xona_jadval_r:"))
async def xona_jadval_rooms_orqa(call: CallbackQuery, state: FSMContext, pool):
    parts = call.data.split(":")
    qavat = int(parts[1])
    bino = parts[2]
    await state.update_data(qavat=qavat, bino=bino)
    xonalar = await get_qavat_xonalari(pool, bino, qavat)
    await call.message.edit_text(
        f"🏢 <b>{bino}-bino, {qavat}-qavat</b>\nHaftalik jadval uchun xonani tanlang:",
        reply_markup=admin_xona_rooms_kb(xonalar, bino, f"admin_xona_bino:{bino}"),
    )
    await call.answer()


# ─── 3. KAFEDRALAR ────────────────────────────────────────────────────────────

@router.message(F.text == "🏛 Kafedralar")
async def kafedralar_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Fakultetni tanlang:", reply_markup=fakultet_kb())


@router.callback_query(F.data == "admin_fak_orqa")
async def admin_fak_orqa(call: CallbackQuery):
    await call.message.edit_text("Fakultetni tanlang:", reply_markup=fakultet_kb())
    await call.answer()


@router.callback_query(F.data.startswith("admin_fak:"))
async def admin_fak(call: CallbackQuery, pool):
    bino = call.data.split(":")[1]
    kafedralar = await get_kafedralar_by_bino(pool, bino)
    fakultet = FAKULTETLAR.get(bino, bino)
    if not kafedralar:
        await call.answer("Kafedralar topilmadi", show_alert=True)
        return
    await call.message.edit_text(
        f"🏢 <b>{fakultet}</b>\n\nKafedrani tanlang:",
        reply_markup=kafedralar_kb(kafedralar),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin_kaf_kor:"))
async def admin_kaf_kor(call: CallbackQuery, pool):
    kafedra_id = int(call.data.split(":")[1])
    kafedra = await get_kafedra(pool, kafedra_id)
    oqituvchilar = await get_kafedra_oqituvchilari(pool, kafedra_id)
    if not kafedra:
        await call.answer("Kafedra topilmadi", show_alert=True)
        return
    bino = kafedra.get("bino", "A")
    if not oqituvchilar:
        await call.message.edit_text(
            f"📌 <b>{kafedra['nomi']}</b>\n\nO'qituvchilar ro'yxati bo'sh.",
            reply_markup=_kb([[("◀️ Kafedralar", f"admin_fak:{bino}")]]),
        )
        await call.answer()
        return
    await call.message.edit_text(
        f"📌 <b>{kafedra['nomi']}</b>\n\nO'qituvchini tanlang:",
        reply_markup=oqituvchilar_kb(oqituvchilar, kafedra_id, bino),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin_oq_orqa:"))
async def admin_oq_orqa(call: CallbackQuery, pool):
    kafedra_id = int(call.data.split(":")[1])
    kafedra = await get_kafedra(pool, kafedra_id)
    oqituvchilar = await get_kafedra_oqituvchilari(pool, kafedra_id)
    bino = kafedra.get("bino", "A") if kafedra else "A"
    if not oqituvchilar:
        await call.message.edit_text(
            f"📌 <b>{kafedra['nomi'] if kafedra else ''}</b>\n\nO'qituvchilar ro'yxati bo'sh.",
            reply_markup=_kb([[("◀️ Kafedralar", f"admin_fak:{bino}")]]),
        )
        await call.answer()
        return
    await call.message.edit_text(
        f"📌 <b>{kafedra['nomi'] if kafedra else ''}</b>\n\nO'qituvchini tanlang:",
        reply_markup=oqituvchilar_kb(oqituvchilar, kafedra_id, bino),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin_oq_kor:"))
async def admin_oq_kor(call: CallbackQuery, pool):
    _, oqituvchi_id_str, kafedra_id_str = call.data.split(":")
    oqituvchi_id = int(oqituvchi_id_str)
    kafedra_id = int(kafedra_id_str)
    o = await get_oqituvchi(pool, oqituvchi_id)
    if not o:
        await call.answer("O'qituvchi topilmadi", show_alert=True)
        return
    darslar = await get_oqituvchi_jadval(pool, oqituvchi_id)
    matn = format_oqituvchi_karta(o) + format_haftalik_jadval(darslar)
    await call.message.edit_text(
        matn,
        reply_markup=oqituvchi_nav_kb(oqituvchi_id, kafedra_id),
    )
    await call.answer()


# ── Tahrirlash ────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_tahrir:"))
async def admin_tahrir_boshlash(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    oqituvchi_id = int(parts[1])
    kafedra_id = int(parts[2])
    await state.update_data(oqituvchi_id=oqituvchi_id, kafedra_id=kafedra_id)
    await call.message.edit_text(
        "Qaysi maydonni tahrirlaysiz?",
        reply_markup=tahrir_maydon_kb(oqituvchi_id),
    )
    await state.set_state(AdminTahrir.maydon_tanlash)
    await call.answer()


@router.callback_query(AdminTahrir.maydon_tanlash, F.data.startswith("admin_maydon:"))
async def admin_maydon_tanlash(call: CallbackQuery, state: FSMContext, pool):
    _, maydon, oqituvchi_id_str = call.data.split(":")
    oqituvchi_id = int(oqituvchi_id_str)
    await state.update_data(maydon=maydon, oqituvchi_id=oqituvchi_id)

    if maydon == "telegram_file_id":
        await call.message.edit_text("📷 Rasm yuboring:")
        await state.set_state(AdminTahrir.yangi_qiymat)
        await call.answer()
        return

    if maydon == "kafedra_id":
        kafedralar = await get_all_kafedralar(pool)
        await call.message.edit_text(
            "📌 Yangi kafedrani tanlang:",
            reply_markup=admin_tahrir_kafedra_kb(kafedralar, oqituvchi_id),
        )
        await call.answer()
        return

    nom = TAHRIR_MAYDON_NOMI.get(maydon, maydon)
    await call.message.edit_text(f"✏️ Yangi {nom} kiriting:")
    await state.set_state(AdminTahrir.yangi_qiymat)
    await call.answer()


@router.callback_query(AdminTahrir.maydon_tanlash, F.data.startswith("admin_tahrir_kaf:"))
async def admin_tahrir_kafedra(call: CallbackQuery, state: FSMContext, pool):
    _, kafedra_id_str, oqituvchi_id_str = call.data.split(":")
    kafedra_id_new = int(kafedra_id_str)
    oqituvchi_id = int(oqituvchi_id_str)
    await update_oqituvchi(pool, oqituvchi_id, "kafedra_id", kafedra_id_new)
    data = await state.get_data()
    await state.clear()
    o = await get_oqituvchi(pool, oqituvchi_id)
    darslar = await get_oqituvchi_jadval(pool, oqituvchi_id)
    kafedra_id_orig = data.get("kafedra_id", kafedra_id_new)
    matn = "✅ Kafedra yangilandi\n\n" + format_oqituvchi_karta(o) + format_haftalik_jadval(darslar)
    await call.message.edit_text(
        matn,
        reply_markup=oqituvchi_nav_kb(oqituvchi_id, kafedra_id_orig),
    )
    await call.answer()


@router.message(AdminTahrir.yangi_qiymat, F.photo)
async def admin_yangi_rasm(message: Message, state: FSMContext, pool):
    data = await state.get_data()
    file_id = message.photo[-1].file_id
    await update_oqituvchi(pool, data["oqituvchi_id"], "telegram_file_id", file_id)
    o = await get_oqituvchi(pool, data["oqituvchi_id"])
    darslar = await get_oqituvchi_jadval(pool, data["oqituvchi_id"])
    kafedra_id = data.get("kafedra_id", o.get("kafedra_id"))
    await state.clear()
    matn = "✅ Rasm yangilandi\n\n" + format_oqituvchi_karta(o) + format_haftalik_jadval(darslar)
    await message.answer(matn, reply_markup=oqituvchi_nav_kb(data["oqituvchi_id"], kafedra_id))


@router.message(AdminTahrir.yangi_qiymat)
async def admin_yangi_qiymat(message: Message, state: FSMContext, pool):
    data = await state.get_data()
    maydon = data["maydon"]
    oqituvchi_id = data["oqituvchi_id"]
    kafedra_id = data.get("kafedra_id")
    qiymat_str = message.text.strip()

    if maydon == "tel_raqam":
        if qiymat_str != "—" and not _tel_valid(qiymat_str):
            await message.answer("❌ Format: +998XXXXXXXXX yoki — (tire):")
            return
        qiymat = None if qiymat_str == "—" else qiymat_str
    elif maydon == "xona_raqam":
        if not qiymat_str.isdigit():
            await message.answer("❌ Faqat raqam kiriting:")
            return
        qiymat = int(qiymat_str)
    elif maydon == "telegram_username":
        qiymat = None if qiymat_str == "—" else qiymat_str.lstrip("@")
    else:
        qiymat = None if qiymat_str == "—" else qiymat_str

    await update_oqituvchi(pool, oqituvchi_id, maydon, qiymat)
    o = await get_oqituvchi(pool, oqituvchi_id)
    darslar = await get_oqituvchi_jadval(pool, oqituvchi_id)
    nom = TAHRIR_MAYDON_NOMI.get(maydon, maydon)
    await state.clear()
    matn = f"✅ {nom} yangilandi\n\n" + format_oqituvchi_karta(o) + format_haftalik_jadval(darslar)
    if not kafedra_id:
        kafedra_id = o.get("kafedra_id", 0)
    await message.answer(matn, reply_markup=oqituvchi_nav_kb(oqituvchi_id, kafedra_id))


# ── O'chirish ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_ochir:"))
async def admin_ochir(call: CallbackQuery, pool):
    parts = call.data.split(":")
    oqituvchi_id = int(parts[1])
    kafedra_id = int(parts[2])
    o = await get_oqituvchi(pool, oqituvchi_id)
    if not o:
        await call.answer("Topilmadi", show_alert=True)
        return
    ism = f"{o['familiya']} {o['ism']}"
    await call.message.edit_text(
        f"⚠️ <b>{ism}</b>ni o'chirasizmi?\nBu amalni qaytarib bo'lmaydi!",
        reply_markup=ochirish_tasdiq_kb(oqituvchi_id, kafedra_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin_ochir_ha:"))
async def admin_ochir_ha(call: CallbackQuery, pool):
    parts = call.data.split(":")
    oqituvchi_id = int(parts[1])
    kafedra_id = int(parts[2])
    await delete_oqituvchi(pool, oqituvchi_id)
    kafedra = await get_kafedra(pool, kafedra_id)
    oqituvchilar = await get_kafedra_oqituvchilari(pool, kafedra_id)
    bino = kafedra.get("bino", "A") if kafedra else "A"
    await call.message.edit_text(
        "✅ O'qituvchi o'chirildi",
        reply_markup=oqituvchilar_kb(oqituvchilar, kafedra_id, bino) if oqituvchilar else _kb([[("◀️ Kafedralar", f"admin_fak:{bino}")]]),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin_ochir_yoq:"))
async def admin_ochir_yoq(call: CallbackQuery, pool):
    parts = call.data.split(":")
    oqituvchi_id = int(parts[1])
    kafedra_id = int(parts[2])
    o = await get_oqituvchi(pool, oqituvchi_id)
    darslar = await get_oqituvchi_jadval(pool, oqituvchi_id)
    matn = format_oqituvchi_karta(o) + format_haftalik_jadval(darslar) if o else "Ma'lumot topilmadi"
    await call.message.edit_text(matn, reply_markup=oqituvchi_nav_kb(oqituvchi_id, kafedra_id))
    await call.answer()


# ─── 4. STATISTIKA ────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Statistika")
async def admin_statistika(message: Message, pool):
    stats = await get_all_stats(pool)
    matn = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats.get('jami_foydalanuvchilar', 0)}</b>\n"
        f"📚 O'qituvchilar: <b>{stats.get('jami_oqituvchilar', 0)}</b>\n"
        f"🏛 Kafedralar: <b>10</b>\n\n"
        f"📈 Bugungi faollik:\n"
        f"So'rovlar: <b>{stats.get('bugun_sorovlar', 0)}</b>\n"
        f"Faol foydalanuvchilar: <b>{stats.get('faol_foydalanuvchilar', 0)}</b>"
    )
    await message.answer(matn, reply_markup=statistika_kb())


_KUN_UZ_HAFTA = {0: 'Du', 1: 'Se', 2: 'Ch', 3: 'Pa', 4: 'Ju', 5: 'Sh', 6: 'Ya'}


@router.callback_query(F.data == "admin_stat_hafta")
async def admin_stat_hafta(call: CallbackQuery, pool):
    kunlik = await get_haftalik_hisobot(pool)
    matn = "📅 <b>Haftalik hisobot (so'nggi 7 kun)</b>\n\n"
    if not kunlik:
        matn += "Ma'lumot yo'q."
    else:
        for row in kunlik:
            kun = row['kun']
            kun_str = kun.strftime('%d.%m.%Y') if hasattr(kun, 'strftime') else str(kun)
            hafta_kuni = _KUN_UZ_HAFTA.get(kun.weekday(), '') if hasattr(kun, 'weekday') else ''
            matn += (
                f"📆 <b>{kun_str} ({hafta_kuni})</b>\n"
                f"  So'rovlar: {row['sorovlar']}\n"
                f"  Faol foydalanuvchilar: {row['faol_users']}\n\n"
            )
    await call.message.edit_text(
        matn,
        reply_markup=_kb([[("◀️ Statistikaga qaytish", "admin_stat_orqa")]]),
    )
    await call.answer()


_USERS_PAGE_SIZE = 10


@router.callback_query(F.data.startswith("admin_stat_users"))
async def admin_stat_users(call: CallbackQuery, pool):
    parts = call.data.split(":")
    page = int(parts[1]) if len(parts) > 1 else 0
    offset = page * _USERS_PAGE_SIZE

    users, jami = await get_all_foydalanuvchilar(pool, offset, _USERS_PAGE_SIZE)
    if not users:
        await call.message.edit_text(
            "👥 Foydalanuvchilar yo'q.",
            reply_markup=_kb([[("◀️ Statistikaga qaytish", "admin_stat_orqa")]]),
        )
        await call.answer()
        return

    matn = f"👥 <b>Foydalanuvchilar ro'yxati</b> (jami: {jami})\n\n"
    for i, u in enumerate(users, start=offset + 1):
        ism = f"{u.get('familiya', '')} {u.get('ism', '')}".strip() or "—"
        tel = u.get('tel_raqam') or '—'
        matn += f"{i}. <b>{ism}</b> | {tel}\n   <code>{u['telegram_id']}</code>\n\n"

    nav = []
    if page > 0:
        nav.append(("◀️ Oldingi", f"admin_stat_users:{page - 1}"))
    if offset + _USERS_PAGE_SIZE < jami:
        nav.append(("Keyingi ▶️", f"admin_stat_users:{page + 1}"))

    rows = []
    if nav:
        rows.append(nav)
    rows.append([("◀️ Statistikaga qaytish", "admin_stat_orqa")])
    await call.message.edit_text(matn, reply_markup=_kb(rows))
    await call.answer()


@router.callback_query(F.data == "admin_stat_orqa")
async def admin_stat_orqa(call: CallbackQuery, pool):
    stats = await get_all_stats(pool)
    matn = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats.get('jami_foydalanuvchilar', 0)}</b>\n"
        f"📚 O'qituvchilar: <b>{stats.get('jami_oqituvchilar', 0)}</b>\n"
        f"🏛 Kafedralar: <b>10</b>\n\n"
        f"📈 Bugungi faollik:\n"
        f"So'rovlar: <b>{stats.get('bugun_sorovlar', 0)}</b>\n"
        f"Faol foydalanuvchilar: <b>{stats.get('faol_foydalanuvchilar', 0)}</b>"
    )
    await call.message.edit_text(matn, reply_markup=statistika_kb())
    await call.answer()


# ─── 5. OMMAVIY XABAR ────────────────────────────────────────────────────────

@router.message(F.text == "📢 Ommaviy xabar")
async def admin_broadcast_start(message: Message, state: FSMContext, pool):
    await state.clear()
    async with pool.acquire() as conn:
        soni = await conn.fetchval("SELECT COUNT(*) FROM foydalanuvchilar")
    await message.answer(
        f"📢 Xabar matnini kiriting:\n<i>({soni} ta foydalanuvchiga yuboriladi)</i>",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AdminXabar.matn)


@router.message(AdminXabar.matn)
async def admin_broadcast_matn(message: Message, state: FSMContext, pool):
    matn = message.text.strip()
    await state.update_data(matn=matn)
    async with pool.acquire() as conn:
        soni = await conn.fetchval("SELECT COUNT(*) FROM foydalanuvchilar")
    await message.answer(
        f"📢 <b>{soni}</b> ta foydalanuvchiga yuboriladi.\nTasdiqlaysizmi?\n\n"
        f"<blockquote>{matn}</blockquote>",
        reply_markup=broadcast_tasdiq_kb(),
    )
    await state.set_state(AdminXabar.tasdiq)


@router.callback_query(AdminXabar.tasdiq, F.data == "admin_broadcast_ha")
async def admin_broadcast_yuborish(call: CallbackQuery, state: FSMContext, pool):
    data = await state.get_data()
    await call.message.edit_text("⏳ Yuborilmoqda...")
    natija = await send_broadcast(pool, call.bot, data["matn"])
    await state.clear()
    await call.message.edit_text(
        f"✅ Yuborildi: <b>{natija['yuborildi']}</b> ta\n"
        f"❌ Xato: <b>{natija['xato']}</b> ta (bloklagan)"
    )
    await call.message.answer("Admin panel:", reply_markup=admin_menu_kb())
    await call.answer()


@router.callback_query(AdminXabar.tasdiq, F.data == "admin_broadcast_yoq")
async def admin_broadcast_bekor(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Bekor qilindi.")
    await call.message.answer("Admin panel:", reply_markup=admin_menu_kb())
    await call.answer()
