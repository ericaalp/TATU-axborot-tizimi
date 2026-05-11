from aiogram.fsm.state import State, StatesGroup


class Royxat(StatesGroup):
    ism = State()
    familiya = State()
    telefon = State()
    tasdiqlash = State()


class Qidiruv(StatesGroup):
    ism_kiritish = State()
    natija_tanlash = State()


class AdminOqituvchi(StatesGroup):
    ism_familiya = State()
    kafedra = State()
    tel = State()
    telegram = State()
    xona_raqam = State()
    bino = State()


class AdminJadval(StatesGroup):
    oqituvchi_qidirish = State()
    oqituvchi_tanlash = State()
    kun = State()
    juft = State()
    xona = State()
    bino = State()
    fan = State()
    guruh = State()


class AdminXonaMenu(StatesGroup):
    amal = State()


class AdminXonaQosh(StatesGroup):
    qavat = State()
    raqam = State()


class AdminXonaBand(StatesGroup):
    qavat = State()   # xonalar ro'yxati ko'rsatiladi
    xona = State()    # xona tanlandi, opsiyalar ko'rsatiladi
    kun = State()     # "band qilish" boshlandi, kun tanlanadi
    juft = State()    # kun tanlandi, juftliklar ko'rsatiladi
    tasdiq = State()  # juft tanlandi, tasdiqlash ekrani


class AdminXonaJadval(StatesGroup):
    qavat = State()
    xona = State()


class AdminTahrir(StatesGroup):
    maydon_tanlash = State()
    yangi_qiymat = State()


class AdminXabar(StatesGroup):
    matn = State()
    tasdiq = State()
