"""
A-bino xonalar + yangi o'qituvchilar + dars jadvali kiritish.
"""
import asyncio
import asyncpg
from datetime import time as dtime

DB_DSN = "postgresql://postgres:2304@localhost:5432/tatu_sf"

def t(s: str) -> dtime:
    h, m = s.split(':')
    return dtime(int(h), int(m))

JUFT = {
    1: (t('08:30'), t('09:50')),
    2: (t('10:00'), t('11:20')),
    3: (t('11:30'), t('12:50')),
    4: (t('13:30'), t('14:50')),
    5: (t('15:00'), t('16:20')),
    6: (t('16:30'), t('17:50')),
}

# ─── Yangi o'qituvchilar ─────────────────────────────────────────────────────
YANGI_OQITUVCHILAR = [
    ('Ijtimoiy gumanitar-1', 'Muhammadiyev', 'H.'),
    ('Ijtimoiy gumanitar-2', 'Achilov',      'Z.'),
]

# ─── A-bino xonalar ──────────────────────────────────────────────────────────
A_XONALAR = [
    # 1-qavat
    (101,1),(102,1),(103,1),(104,1),(105,1),(106,1),
    (107,1),(108,1),(109,1),(110,1),(112,1),
    # 2-qavat
    (201,2),(202,2),(203,2),(204,2),(205,2),(206,2),(207,2),(208,2),
    (209,2),(210,2),(211,2),(212,2),(213,2),(214,2),(215,2),(217,2),
    (218,2),(219,2),(220,2),(221,2),(226,2),(227,2),(228,2),(229,2),(230,2),
    # 3-qavat
    (301,3),(302,3),(303,3),(304,3),(305,3),(306,3),(307,3),(308,3),
    (309,3),(310,3),(311,3),(312,3),(313,3),(314,3),(315,3),(316,3),
    (317,3),(318,3),(319,3),(320,3),(321,3),(325,3),(326,3),(327,3),
    (328,3),(329,3),(330,3),(331,3),
]

# ─── Dars jadvali ────────────────────────────────────────────────────────────
# (familiya_lookup, xona_raqam, fan_nomi, guruh, kun, juft)
DARSLAR = [
    # ══════════════════════════════════
    # 3-KURS  RUS GURUHLARI
    # ══════════════════════════════════

    # ── AKT23-03 ──
    ('Ganiyeva',    314, 'Raqamli texnologiya va innovatsiyalar (m)',    'AKT23-03', 'dushanba', 4),
    ('Ganiyeva',    314, 'Raqamli texnologiya va innovatsiyalar (a)',    'AKT23-03', 'dushanba', 5),
    ('Ganiyeva',    321, 'Kreativ pedagogika (m)',                       'AKT23-03', 'seshanba', 4),
    ('Ganiyeva',    321, 'Kreativ pedagogika (a)',                       'AKT23-03', 'seshanba', 5),
    ('Axmedjanov',  201, 'Moliyaviy savodxonlik/Pedagogika/Atrof-muhit (m)', 'AKT23-03', 'chorshanba', 4),
    ('Axmedjanov',  201, 'Moliyaviy savodxonlik/Pedagogika/Atrof-muhit (a)', 'AKT23-03', 'chorshanba', 5),
    ('Raxmonov_X',  321, "O'rnatilgan tizimlar (m)",                    'AKT23-03', 'payshanba', 2),
    ('Raxmonov_X',  321, "O'rnatilgan tizimlar (m)",                    'AKT23-03', 'payshanba', 3),
    ('Normatova',   328, 'Individual loyiha',                           'AKT23-03', 'juma', 2),
    ('Ismoilov_I',  217, "O'rnatilgan tizimlar (a)",                    'AKT23-03', 'juma', 3),
    ('Normatova',   331, 'Individual loyiha',                           'AKT23-03', 'juma', 4),

    # ── TT23-07 ──
    ('Xodjayev',    221, 'Individual loyiha',                           'TT23-07', 'seshanba', 4),
    ('Xidirov',     221, "O'rnatilgan boshqaruv tizimlar (m)",          'TT23-07', 'seshanba', 5),
    ('Xidirov',     221, 'Simsiz tarmoqlar (a)',                        'TT23-07', 'chorshanba', 3),
    ('Xodjayev',    221, 'Individual loyiha',                           'TT23-07', 'chorshanba', 3),
    ('Xidirov',     221, 'Simsiz tarmoqlar (m)',                        'TT23-07', 'payshanba', 4),
    ('Xidirov',     221, "O'rnatilgan boshqaruv tizimlar (a)",          'TT23-07', 'payshanba', 5),
    ('Raximov_A',   214, 'IoT aloqa va protokollari (m)',               'TT23-07', 'juma', 1),
    ('Raximov_A',   214, 'IoT aloqa va protokollari (a)',               'TT23-07', 'juma', 2),
    ('Raximov_A',   214, 'IoT aloqa va protokollari (m)',               'TT23-07', 'juma', 3),
    ('Xidirov',     214, "O'rnatilgan boshqaruv tizimlar (m)",          'TT23-07', 'juma', 3),

    # ── AX23-09 ──
    ('Xasanov',     217, 'Server Administration (m)',                   'AX23-09', 'dushanba', 4),
    ('Xasanov',     317, 'Server Administration (m)',                   'AX23-09', 'dushanba', 5),
    ('Kiyamov',     108, 'Individual loyiha',                          'AX23-09', 'seshanba', 4),
    ('Xaqberdiyev', 317, "O'rnatilgan tizimlar (a)",                    'AX23-09', 'seshanba', 5),
    ('Raxmonov_X',  321, "O'rnatilgan tizimlar (m)",                    'AX23-09', 'payshanba', 2),
    ('Raxmonov_X',  321, "O'rnatilgan tizimlar (m)",                    'AX23-09', 'payshanba', 3),
    ('Kiyamov',     307, 'Server Administration (a)',                   'AX23-09', 'juma', 1),
    ('Sharipova',   314, 'Tarmoq xavfsizligi (a)',                      'AX23-09', 'juma', 2),
    ('Kiyamov',     227, 'Tarmoq xavfsizligi (m)',                     'AX23-09', 'juma', 4),
    ('Kiyamov',     307, 'Server Administration (a)',                   'AX23-09', 'juma', 5),

    # ── RI23-11 ──
    ('Abdukarimova',313, 'Moliya bozori (m)',                           'RI23-11', 'dushanba', 3),
    ('Qudratova',   313, "Sug'urta ishi (m)",                          'RI23-11', 'dushanba', 4),
    ('Qudratova',   313, "Sug'urta ishi (a)",                          'RI23-11', 'dushanba', 5),
    ('Latipov',     227, 'Raqamli iqtisodiyot va innovatsiya (m)',      'RI23-11', 'seshanba', 4),
    ('Latipov',     230, 'Raqamli iqtisodiyot va innovatsiya (m)',      'RI23-11', 'seshanba', 5),
    ('Abdukarimova',321, 'Moliya bozori (m)',                           'RI23-11', 'payshanba', 4),
    ('Qudratova',   321, "Sug'urta ishi (m)",                          'RI23-11', 'payshanba', 4),
    ('Abdukarimova',316, 'Individual loyiha',                          'RI23-11', 'payshanba', 5),
    ('Abdukarimova',325, 'Moliya bozori (a)',                           'RI23-11', 'juma', 2),

    # ══════════════════════════════════
    # 1-KURS  TT25-01, TT25-02, TT25-03
    # ══════════════════════════════════

    # ── TT25-01 va TT25-02 umumiy ──
    ('Dustmurodov', 214, 'Fizika (m)',                                  'TT25-01', 'dushanba', 2),
    ('Dustmurodov', 214, 'Fizika (m)',                                  'TT25-02', 'dushanba', 2),
    ('Bolbekov',    227, 'Muhammandislik grafikasi (m)',                'TT25-01', 'dushanba', 3),
    ('Bolbekov',    227, 'Muhammandislik grafikasi (m)',                'TT25-02', 'dushanba', 3),
    ('Muhammadiyev_H',112,"O'zbekistonning eng yangi tarixi (m)",      'TT25-01', 'dushanba', 4),
    ('Muhammadiyev_H',112,"O'zbekistonning eng yangi tarixi (m)",      'TT25-02', 'dushanba', 4),
    ('Juraqulov',   112, 'Hisob (calculus) 2 (m)',                     'TT25-01', 'seshanba', 2),
    ('Juraqulov',   112, 'Hisob (calculus) 2 (m)',                     'TT25-02', 'seshanba', 2),
    ('Kubayeva_Sh', 112, 'Dinshunoslik (m)',                           'TT25-01', 'seshanba', 3),
    ('Kubayeva_Sh', 112, 'Dinshunoslik (m)',                           'TT25-02', 'seshanba', 3),
    ('Muhammadiyev_H',127,"O'zbekistonning eng yangi tarixi (m)",      'TT25-01', 'chorshanba', 3),
    ('Muhammadiyev_H',127,"O'zbekistonning eng yangi tarixi (m)",      'TT25-02', 'chorshanba', 3),
    ('Bolbekov',    328, 'Muhammandislik grafikasi (a)',               'TT25-01', 'payshanba', 2),
    ('Bolbekov',    328, 'Muhammandislik grafikasi (a)',               'TT25-02', 'payshanba', 2),
    ('Juraqulov',   112, 'Hisob (calculus) 2 (m)',                     'TT25-01', 'payshanba', 3),
    ('Juraqulov',   112, 'Hisob (calculus) 2 (m)',                     'TT25-02', 'payshanba', 3),

    # ── TT25-01 alohida ──
    ('Muhammadiyev_H',230,"O'zbekistonning eng yangi tarixi (a)",      'TT25-01', 'chorshanba', 1),
    ('Kubayeva_Sh', 230, 'Dinshunoslik (s)',                           'TT25-01', 'chorshanba', 2),
    ('Shokirov_F',  316, 'Dasturlash 2 (a)',                           'TT25-01', 'payshanba', 4),
    ('Diyorov',     226, 'Hisob (calculus) (a)',                       'TT25-01', 'juma', 1),
    ('Azimov_U',    311, 'Fizika 2 (a)',                               'TT25-01', 'juma', 2),

    # ── TT25-02 alohida ──
    ('Kubayeva_Sh', 317, 'Dinshunoslik (s)',                           'TT25-02', 'chorshanba', 1),
    ('Maxmidov',    314, 'Dasturlash (a)',                             'TT25-02', 'chorshanba', 2),
    ('Muhammadiyev_H',317,"O'zbekistonning eng yangi tarixi (a)",      'TT25-02', 'chorshanba', 4),
    ('Azimov_U',    227, 'Fizika 2 (a)',                               'TT25-02', 'juma', 1),
    ('Bolbekov',    215, 'Muhammandislik grafikasi (a)',               'TT25-02', 'juma', 2),
    ('Tursunov',    315, 'Dasturlash 2 (m)',                           'TT25-02', 'juma', 3),

    # ── TT25-03 alohida ──
    # Seshanba: Xorijiy til 2 (teachers + rooms)
    ('Kabilova',    301, 'Xorijiy til 2',                              'TT25-03', 'seshanba', 1),
    ('Toshpulatov', 311, 'Xorijiy til 2',                              'TT25-03', 'seshanba', 1),
    ('Narziyeva',   317, 'Xorijiy til 2',                              'TT25-03', 'seshanba', 1),
    ('Ibatova',     313, 'Xorijiy til 2',                              'TT25-03', 'seshanba', 1),
    ('Akromova',    331, 'Xorijiy til 2',                              'TT25-03', 'seshanba', 1),
    ('Indiaminov',  331, 'Hisob (calculus) (a)',                       'TT25-03', 'chorshanba', 2),
    # Payshanba: Xorijiy til 2
    ('Kabilova',    328, 'Xorijiy til 2',                              'TT25-03', 'payshanba', 1),
    ('Toshpulatov', 316, 'Xorijiy til 2',                              'TT25-03', 'payshanba', 1),
    ('Narziyeva',   325, 'Xorijiy til 2',                              'TT25-03', 'payshanba', 1),
    ('Ibatova',     315, 'Xorijiy til 2',                              'TT25-03', 'payshanba', 1),
    ('Akromova',    313, 'Xorijiy til 2',                              'TT25-03', 'payshanba', 1),
    ('Rajabov_J',   301, 'Fizika 2 (a)',                               'TT25-03', 'payshanba', 2),
    ('Muhammadiyev_H',315,"O'zbekistonning eng yangi tarixi (a)",      'TT25-03', 'payshanba', 4),
    ('Bolbekov',    230, 'Muhammandislik grafikasi (a)',               'TT25-03', 'juma', 1),
    ('Tursunov',    315, 'Dasturlash 2 (a)',                           'TT25-03', 'juma', 2),
    ('Tursunov',    226, 'Dasturlash 2 (m)',                           'TT25-03', 'juma', 3),

    # ══════════════════════════════════
    # 2-KURS  IQ24-08, IQ24-09
    # ══════════════════════════════════

    # ── IQ24-08 va IQ24-09 umumiy (teacher ma'lum bo'lgan qatorlar) ──
    # Seshanba: Korxona iqtisodiyoti / Raqamli iqtisodiyot
    ('Abdullayev',  315, 'Korxona iqtisodiyoti (m)',                   'IQ24-08', 'seshanba', 4),
    ('Baxodirov',   316, 'Raqamli iqtisodiyot (m)',                    'IQ24-08', 'seshanba', 4),
    ('Abdullayev',  315, 'Korxona iqtisodiyoti (a)',                   'IQ24-08', 'seshanba', 5),
    ('Baxodirov',   316, 'Raqamli iqtisodiyot (a)',                    'IQ24-08', 'seshanba', 5),
    ('Abdullayev',  315, 'Korxona iqtisodiyoti (m)',                   'IQ24-09', 'seshanba', 4),
    ('Baxodirov',   316, 'Raqamli iqtisodiyot (m)',                    'IQ24-09', 'seshanba', 4),
    ('Abdullayev',  315, 'Korxona iqtisodiyoti (a)',                   'IQ24-09', 'seshanba', 5),
    ('Baxodirov',   316, 'Raqamli iqtisodiyot (a)',                    'IQ24-09', 'seshanba', 5),
    # Chorshanba
    ('Achilov_Z',   311, "Pul, kredit va banklar (m)",                 'IQ24-08', 'chorshanba', 3),
    ('Ismoilova',   331, "Sug'urta (m)",                               'IQ24-08', 'chorshanba', 3),
    ('Abdullayev',  317, 'Tadbirkorlik va biznes (m)',                  'IQ24-08', 'chorshanba', 4),
    ('Achilov_S',   311, 'Buxalteriya hisobi (m)',                     'IQ24-08', 'chorshanba', 4),
    ('Achilov_Z',   302, "Pul, kredit va banklar (a)",                 'IQ24-08', 'chorshanba', 5),
    ('Ismoilova',   314, "Sug'urta (a)",                               'IQ24-08', 'chorshanba', 5),
    ('Achilov_Z',   311, "Pul, kredit va banklar (m)",                 'IQ24-09', 'chorshanba', 3),
    ('Ismoilova',   331, "Sug'urta (m)",                               'IQ24-09', 'chorshanba', 3),
    ('Abdullayev',  317, 'Tadbirkorlik va biznes (m)',                  'IQ24-09', 'chorshanba', 4),
    ('Achilov_S',   311, 'Buxalteriya hisobi (m)',                     'IQ24-09', 'chorshanba', 4),
    ('Achilov_Z',   302, "Pul, kredit va banklar (a)",                 'IQ24-09', 'chorshanba', 5),
    ('Ismoilova',   314, "Sug'urta (a)",                               'IQ24-09', 'chorshanba', 5),
    # Payshanba
    ('Abdullayev',  316, 'Tadbirkorlik va biznes (a)',                  'IQ24-08', 'payshanba', 3),
    ('Achilov_S',   315, 'Buxalteriya hisobi (a)',                     'IQ24-08', 'payshanba', 3),
    ('Abdullayev',  316, 'Tadbirkorlik va biznes (a)',                  'IQ24-09', 'payshanba', 3),
    ('Achilov_S',   315, 'Buxalteriya hisobi (a)',                     'IQ24-09', 'payshanba', 3),

    # ── IQ24-08 alohida ──
    ('Xoliyarova',  311, 'Amaliy ekonometrika (m)',                    'IQ24-08', 'dushanba', 3),
    ('Ismoilova',   226, 'Mikroiqtisodiyot 2 (a)',                     'IQ24-08', 'payshanba', 1),
    ('Normatova',   201, 'Amaliy ekonometrika (a)',                    'IQ24-08', 'juma', 3),
    ('Baxodirov',   201, 'Makroiqtisodiyot (a)',                       'IQ24-08', 'juma', 4),

    # ── IQ24-09 alohida ──
    ('Ismoilova',   301, 'Mikroiqtisodiyot 2 (m)',                     'IQ24-09', 'dushanba', 4),
    ('Baxodirov',   301, 'Makroiqtisodiyot (m)',                       'IQ24-09', 'dushanba', 5),
    ('Ismoilova',   217, 'Mikroiqtisodiyot 2 (a)',                     'IQ24-09', 'payshanba', 2),
    ('Baxodirov',   307, 'Makroiqtisodiyot (a)',                       'IQ24-09', 'juma', 2),
    ('Xoliyarova',  321, 'Amaliy ekonometrika (a)',                    'IQ24-09', 'juma', 3),

    # ══════════════════════════════════
    # 4-KURS  PA22-10
    # ══════════════════════════════════
    ('Gayratov',    315, 'Pochta aloqasida texnologik injiniring (A)', 'PA22-10', 'dushanba', 1),
    ('Baxodirov',   315, 'Yetkazib berishni boshqarish (M)',           'PA22-10', 'dushanba', 2),
    ('Baxodirov',   315, 'Yetkazib berishni boshqarish (A)',           'PA22-10', 'dushanba', 3),
    ('Baxodirov',   315, 'Yetkazib berishni boshqarish (M)',           'PA22-10', 'seshanba', 1),
    ('Baxodirov',   315, 'Yetkazib berishni boshqarish (A)',           'PA22-10', 'seshanba', 2),
    ('Mavlonov_U',  214, 'Pochta aloqasida texnologik injiniring (M)', 'PA22-10', 'chorshanba', 1),
    ('Mavlonov_U',  214, 'Pochta aloqasida texnologik injiniring (M)', 'PA22-10', 'chorshanba', 2),
    ('Gayratov',    214, 'Pochta aloqasida texnologik injiniring (A)', 'PA22-10', 'chorshanba', 3),
]

# familiya_lookup → DB familiya
FAMILIYA_MAP = {
    'Raxmonov_X':    'Raxmonov',
    'Ismoilov_I':    'Ismoilov',
    'Raximov_A':     'Raximov',
    'Kubayeva_Sh':   'Kubayeva',
    'Shokirov_F':    'Shokirov',
    'Rajabov_J':     'Rajabov',
    'Azimov_U':      'Azimov',
    'Muhammadiyev_H':'Muhammadiyev',
    'Achilov_Z':     'Achilov',
    'Achilov_S':     'Achilov',
    'Xoliyarova':    'Xoliyarova',
    "Gayratov":      "G'ayratov",
    'Mavlonov_U':    'Mavlonov',
    'Dustmurodov':   'Dustmurodov',
    'Xaqberdiyev':   'Xaqberdiyev',
}

# lookup_key → (familiya, kafedra_id)
FAMILIYA_KAFEDRA = {
    'Raxmonov_X':    ('Raxmonov',   9),
    'Ismoilov_I':    ('Ismoilov',   5),
    'Raximov_A':     ('Raximov',    8),
    'Kubayeva_Sh':   ('Kubayeva',   2),
    'Shokirov_F':    ('Shokirov',   9),
    'Rajabov_J':     ('Rajabov',    4),
    'Azimov_U':      ('Azimov',     4),
    'Muhammadiyev_H':('Muhammadiyev',2),
    'Achilov_S':     ('Achilov',    3),
    'Xoliyarova':    ('Xoliyarova', 9),
    "Gayratov":      ("G'ayratov",  8),
    'Mavlonov_U':    ('Mavlonov',   8),
}

# Ism bilan aniqlashtirish (bir xil familiya + kafedra_id bo'lganda)
FAMILIYA_ISM = {
    'Achilov_Z': ('Achilov', 'Z.'),
    'Achilov_S': ('Achilov', 'S.'),
}


async def main():
    conn = await asyncpg.connect(DB_DSN)
    try:
        # ── 0. Eski A-bino ma'lumotlarni tozalash ────────────────────────────
        deleted = await conn.fetchval("SELECT COUNT(*) FROM dars_jadvali WHERE bino='A'")
        await conn.execute("DELETE FROM dars_jadvali WHERE bino='A'")
        await conn.execute("DELETE FROM xonalar WHERE bino='A'")
        print(f"Eski A-bino darslar o'chirildi: {deleted} ta")

        # ── 1. Xonalar ────────────────────────────────────────────────────────
        await conn.executemany(
            "INSERT INTO xonalar (raqam, bino, qavat) VALUES ($1, 'A', $2)",
            A_XONALAR
        )
        print(f"{len(A_XONALAR)} ta A-bino xona qo'shildi")

        # ── 2. Yangi o'qituvchilar ─────────────────────────────────────────────
        inserted = 0
        for kafedra_nomi, familiya, ism in YANGI_OQITUVCHILAR:
            kafedra_id = await conn.fetchval(
                "SELECT id FROM kafedralar WHERE nomi=$1", kafedra_nomi
            )
            exists = await conn.fetchval(
                "SELECT id FROM oqituvchilar WHERE familiya=$1 AND ism=$2 AND kafedra_id=$3",
                familiya, ism, kafedra_id
            )
            if not exists:
                await conn.execute(
                    """INSERT INTO oqituvchilar
                       (kafedra_id, familiya, ism, bino, faol)
                       VALUES ($1, $2, $3, 'A', TRUE)""",
                    kafedra_id, familiya, ism
                )
                inserted += 1
        print(f"{inserted} ta yangi o'qituvchi qo'shildi")

        # ── 3. ID lug'ati ─────────────────────────────────────────────────────
        rows = await conn.fetch(
            "SELECT id, familiya, ism, kafedra_id FROM oqituvchilar WHERE faol=TRUE"
        )
        fam_to_id: dict[str, int] = {}
        fam_kafedra_to_id: dict[tuple, int] = {}
        fam_ism_to_id: dict[tuple, int] = {}

        for r in rows:
            fam = r['familiya']
            kid = r['kafedra_id']
            ism = r['ism']
            oid = r['id']
            if fam not in fam_to_id:
                fam_to_id[fam] = oid
            fam_kafedra_to_id[(fam, kid)] = oid
            fam_ism_to_id[(fam, ism)] = oid

        def lookup(key: str) -> int | None:
            # 1. Ism bilan aniq topish
            if key in FAMILIYA_ISM:
                real_fam, real_ism = FAMILIYA_ISM[key]
                result = fam_ism_to_id.get((real_fam, real_ism))
                if result:
                    return result
            # 2. (familiya, kafedra_id) bilan topish
            if key in FAMILIYA_KAFEDRA:
                real_fam, kid = FAMILIYA_KAFEDRA[key]
                result = fam_kafedra_to_id.get((real_fam, kid))
                if result:
                    return result
            # 3. familiya bo'yicha oddiy topish
            real_fam = FAMILIYA_MAP.get(key, key)
            return fam_to_id.get(real_fam)

        # ── 4. Dars jadvali ───────────────────────────────────────────────────
        dars_rows = []
        not_found = set()
        for (fam_key, xona, fan, guruh, kun, juft) in DARSLAR:
            oid = lookup(fam_key)
            if not oid:
                not_found.add(fam_key)
                continue
            bosh, tug = JUFT[juft]
            dars_rows.append((oid, xona, 'A', fan, guruh, kun, bosh, tug))

        if not_found:
            print(f"TOPILMADI: {not_found}")

        await conn.executemany(
            """INSERT INTO dars_jadvali
               (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
            dars_rows
        )
        print(f"{len(dars_rows)} ta dars jadvali yozuvi qo'shildi")

        # ── 5. Tekshirish ─────────────────────────────────────────────────────
        xona_cnt = await conn.fetchval("SELECT COUNT(*) FROM xonalar WHERE bino='A'")
        dars_cnt = await conn.fetchval("SELECT COUNT(*) FROM dars_jadvali WHERE bino='A'")

        qavat = await conn.fetch(
            "SELECT qavat, COUNT(*) AS soni FROM xonalar WHERE bino='A' GROUP BY qavat ORDER BY qavat"
        )
        print(f"\nNatija:")
        print(f"  A-bino xonalar: {xona_cnt}")
        for r in qavat:
            print(f"    {r['qavat']}-qavat: {r['soni']} xona")
        print(f"  A-bino darslar: {dars_cnt}")

        kun_stat = await conn.fetch(
            """SELECT kun, COUNT(*) AS soni FROM dars_jadvali WHERE bino='A'
               GROUP BY kun ORDER BY CASE kun
               WHEN 'dushanba' THEN 1 WHEN 'seshanba' THEN 2
               WHEN 'chorshanba' THEN 3 WHEN 'payshanba' THEN 4 WHEN 'juma' THEN 5 END"""
        )
        for r in kun_stat:
            print(f"    {r['kun']:12s}: {r['soni']}")

        top = await conn.fetch(
            """SELECT o.familiya, COUNT(d.id) AS soni
               FROM dars_jadvali d
               JOIN oqituvchilar o ON o.id=d.oqituvchi_id
               WHERE d.bino='A'
               GROUP BY o.familiya ORDER BY soni DESC LIMIT 20"""
        )
        print("\nKo'p dars beradiganlar (top-20):")
        for r in top:
            print(f"  {r['familiya']:20s} {r['soni']:3d} ta")

    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
