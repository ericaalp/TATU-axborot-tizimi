from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
)


def asosiy_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏛 Kafedralar"), KeyboardButton(text="🚪 Xona holati")],
            [KeyboardButton(text="🔍 Domla qidirish")],
        ],
        resize_keyboard=True,
        persistent=True,
    )


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


def telefon_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def binolar_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏢 A-bino", callback_data="bino:A"),
        InlineKeyboardButton(text="🏢 B-bino", callback_data="bino:B"),
    ]])


def kafedralar_inline_kb(kafedralar: list[dict], bino: str) -> InlineKeyboardMarkup:
    rows = []
    for k in kafedralar:
        rows.append([InlineKeyboardButton(
            text=k["nomi"],
            callback_data=f"kafedra:{k['id']}"
        )])
    rows.append([InlineKeyboardButton(text="◀️ Binolar", callback_data="binolar")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def oqituvchilar_inline_kb(oqituvchilar: list[dict], kafedra_id: int) -> InlineKeyboardMarkup:
    rows = []
    for o in oqituvchilar:
        ism_qisqa = (o["ism"][0] + ".") if o.get("ism") else ""
        rows.append([InlineKeyboardButton(
            text=f"{o['familiya']} {ism_qisqa}",
            callback_data=f"oqituvchi:{o['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text="◀️ Kafedralar",
        callback_data=f"kafedralar:{kafedra_id}"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def oqituvchi_nav_kb(kafedra_id: int, file_id: str = None) -> InlineKeyboardMarkup:
    rows = []
    if file_id:
        rows.append([InlineKeyboardButton(
            text="📷 Rasm",
            callback_data="rasm:" + file_id
        )])
    rows.append([
        InlineKeyboardButton(text="◀️ Kafedraga qaytish", callback_data=f"kafedraga:{kafedra_id}"),
        InlineKeyboardButton(text="🔍 Qidiruv", callback_data="qidiruv_boshla"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def qavatlar_inline_kb(bino: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="1-qavat", callback_data=f"qavat:{bino}:1"),
        InlineKeyboardButton(text="2-qavat", callback_data=f"qavat:{bino}:2"),
        InlineKeyboardButton(text="3-qavat", callback_data=f"qavat:{bino}:3"),
    ]])


def xonalar_inline_kb(xonalar: list[dict], bino: str, qavat: int) -> InlineKeyboardMarkup:
    rows = []
    qator = []
    for x in xonalar:
        belgi = "🔴" if x["band"] else "✅"
        qator.append(InlineKeyboardButton(
            text=f"{belgi} {x['raqam']}",
            callback_data=f"xona:{x['raqam']}:{bino}"
        ))
        if len(qator) == 3:
            rows.append(qator)
            qator = []
    if qator:
        rows.append(qator)
    rows.append([InlineKeyboardButton(text="◀️ Qavatlar", callback_data="xbino:" + bino)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def qidiruv_natijalari_kb(oqituvchilar: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for o in oqituvchilar:
        ism_qisqa = (o["ism"][0] + ".") if o.get("ism") else ""
        kafedra_nomi = o.get("kafedra_nomi", "")
        rows.append([InlineKeyboardButton(
            text=f"{o['familiya']} {ism_qisqa} — {kafedra_nomi}",
            callback_data=f"qidiruv:{o['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tasdiqlash_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Saqlash", callback_data="tasdiq:ha"),
        InlineKeyboardButton(text="✏️ Qayta kiritish", callback_data="tasdiq:yoq"),
    ]])


def kun_tanlash_kb() -> InlineKeyboardMarkup:
    kunlar = [
        ("Du", "dushanba"), ("Se", "seshanba"), ("Ch", "chorshanba"),
        ("Pa", "payshanba"), ("Ju", "juma"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=q, callback_data="kun:" + k) for q, k in kunlar
    ]])


def bino_tanlash_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="A-bino", callback_data="adm_bino:A"),
        InlineKeyboardButton(text="B-bino", callback_data="adm_bino:B"),
    ]])


def tahrir_maydon_kb(oqituvchi_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ism", callback_data=f"maydon:ism:{oqituvchi_id}"),
            InlineKeyboardButton(text="Telefon", callback_data=f"maydon:tel_raqam:{oqituvchi_id}"),
        ],
        [
            InlineKeyboardButton(text="Telegram", callback_data=f"maydon:telegram_username:{oqituvchi_id}"),
            InlineKeyboardButton(text="Kafedra", callback_data=f"maydon:kafedra_id:{oqituvchi_id}"),
        ],
        [
            InlineKeyboardButton(text="Xona", callback_data=f"maydon:xona_raqam:{oqituvchi_id}"),
            InlineKeyboardButton(text="Rasm", callback_data=f"maydon:telegram_file_id:{oqituvchi_id}"),
        ],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"ochir:{oqituvchi_id}")],
    ])


def ochirish_tasdiq_kb(oqituvchi_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, o'chir", callback_data=f"ochir_ha:{oqituvchi_id}"),
        InlineKeyboardButton(text="❌ Bekor", callback_data=f"ochir_yoq:{oqituvchi_id}"),
    ]])


def admin_kafedra_tanlash_kb(kafedralar: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for k in kafedralar:
        rows.append([InlineKeyboardButton(
            text=k["nomi"],
            callback_data=f"adm_kafedra:{k['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def xona_holat_kb(raqam: int, bino: str, band: bool) -> InlineKeyboardMarkup:
    if band:
        tugma = InlineKeyboardButton(text="✅ Bo'sh qilish", callback_data=f"holat_bosh:{raqam}:{bino}")
    else:
        tugma = InlineKeyboardButton(text="🔴 Band qilish", callback_data=f"holat_band:{raqam}:{bino}")
    return InlineKeyboardMarkup(inline_keyboard=[[tugma]])
