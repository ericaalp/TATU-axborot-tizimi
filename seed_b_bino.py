"""
B-bino xonalar + yangi o'qituvchilar + dars jadvali kiritish.
"""
import asyncio
import asyncpg
from datetime import time as dtime

def t(s: str) -> dtime:
    h, m = s.split(':')
    return dtime(int(h), int(m))

DB_DSN = "postgresql://postgres:2304@localhost:5432/tatu_sf"

# Vaqt jufti → (boshlanish, tugash)
JUFT = {
    1: (t('08:30'), t('09:50')),
    2: (t('10:00'), t('11:20')),
    3: (t('11:30'), t('12:50')),
    4: (t('13:30'), t('14:50')),
    5: (t('15:00'), t('16:20')),
    6: (t('16:30'), t('17:50')),
}

# ─── Yangi o'qituvchilar ─────────────────────────────────────────────────────
# (kafedra_nomi, familiya, ism)
YANGI_OQITUVCHILAR = [
    # Kompyuter tizimlari (kafedra_id=7)
    ('Kompyuter tizimlari', 'Toshboyev',    'J.'),
    ('Kompyuter tizimlari', 'Mirsaidov',    'B.'),
    ('Kompyuter tizimlari', 'Nazarov',      'B.'),
    ('Kompyuter tizimlari', 'Abdiyeva',     'X.'),
    ('Kompyuter tizimlari', 'Erkinov',      'J.'),
    ('Kompyuter tizimlari', 'Obloqulov',    'S.'),
    ('Kompyuter tizimlari', 'Boymurodov',   'J.'),
    ('Kompyuter tizimlari', 'Absalomov',    'A.'),
    ('Kompyuter tizimlari', 'Muminov',      'U.'),
    ('Kompyuter tizimlari', 'Niyozov',      'I.'),
    ('Kompyuter tizimlari', 'Buriboyev',    'A.'),
    ('Kompyuter tizimlari', 'Ubaydullayev', 'M.'),
    ('Kompyuter tizimlari', "To'xtayeva",   'M.'),
    ('Kompyuter tizimlari', 'Bobobekova',   'H.'),
    ('Kompyuter tizimlari', 'Eshonqulov',   'E.'),
    ('Kompyuter tizimlari', 'Hakimov',      'J.'),
    ('Kompyuter tizimlari', 'Narmuradov',   'U.'),
    ('Kompyuter tizimlari', 'Jumanov',      'V.'),
    # Dasturiy injiniring (kafedra_id=6)
    ('Dasturiy injiniring', 'Murodov',      'F.'),
]

# ─── B-bino xonalar ──────────────────────────────────────────────────────────
B_XONALAR = [
    # (raqam, qavat)
    (1, 0), (2, 0), (3, 0), (4, 0),
    (100, 1), (101, 1), (102, 1), (103, 1), (104, 1), (108, 1), (116, 1),
    (201, 2), (202, 2), (204, 2), (207, 2), (214, 2), (215, 2),
    (218, 2), (219, 2), (220, 2),
    (301, 3), (302, 3), (305, 3), (307, 3), (308, 3), (312, 3),
    (313, 3), (314, 3), (316, 3), (317, 3),
]

# ─── Dars jadvali ────────────────────────────────────────────────────────────
# Har entry: (familiya_lookup, xona_raqam, fan_nomi, guruh, kun, juft_raqami)
# familiya_lookup = familiya yoki None (keyinroq izoh)
# Multi-teacher entries alohida satrlar sifatida yozilgan.

DARSLAR = [
    # ══════════════════════════════════
    # 3-KURS  6-SEMESTR
    # ══════════════════════════════════

    # ── KI23-01 ──
    ('Mamaraufov', 201, 'Multiagent tizimlar (a)',                  'KI23-01', 'dushanba', 4),
    ('Norqulov',   204, "Ma'lumotlarning intellektual tahlili (a)", 'KI23-01', 'dushanba', 5),
    ('Davronov',     2, 'Hayot faoliyati xavfsizligi/Metrologiya (m)', 'KI23-01', 'seshanba', 4),
    ('Dustmurodov',  3, 'Hayot faoliyati xavfsizligi/Metrologiya (m)', 'KI23-01', 'seshanba', 4),
    ('Primova',    308, "O'rnatilgan tizimlar (m)",                 'KI23-01', 'seshanba', 5),
    ('Norqulov',   204, "Ma'lumotlarning intellektual tahlili (m)", 'KI23-01', 'chorshanba', 4),
    ('Mirsaidov',  302, "O'rnatilgan tizimlar (a)",                 'KI23-01', 'chorshanba', 5),
    ('Mamaraufov', 207, 'Multiagent tizimlar (m)',                  'KI23-01', 'payshanba', 4),
    ('Primova',    308, "O'rnatilgan tizimlar (m)",                 'KI23-01', 'payshanba', 5),
    ('Axrorov',    220, 'Individual loyiha',                        'KI23-01', 'juma', 4),
    ('Axrorov',    101, 'Individual loyiha',                        'KI23-01', 'juma', 5),

    # ── KI23-02 ──
    ('Norqulov',   204, "Ma'lumotlarning intellektual tahlili (a)", 'KI23-02', 'dushanba', 4),
    ('Sattorov',   317, 'Individual loyiha',                        'KI23-02', 'dushanba', 5),
    ('Mamaraufov', 201, 'Multiagent tizimlar (a)',                  'KI23-02', 'juma', 3),
    ('Sattorov',   307, 'Individual loyiha',                        'KI23-02', 'juma', 4),

    # ── KI23-03 ──
    ('Xamiyev',    313, 'Individual loyiha',                        'KI23-03', 'dushanba', 4),
    ('Mamaraufov', 308, 'Multiagent tizimlar (a)',                  'KI23-03', 'dushanba', 5),
    ('Mamaraufov', 204, 'Multiagent tizimlar (m)',                  'KI23-03', 'chorshanba', 3),
    ('Xamiyev',    201, "Ma'lumotlar kommunikatsiyasi (a)",         'KI23-03', 'chorshanba', 5),
    ('Primova',    308, "O'rnatilgan tizimlar (m)",                 'KI23-03', 'payshanba', 4),
    ('Xamiyev',    207, 'Individual loyiha',                        'KI23-03', 'payshanba', 5),
    ('Xamiyev',    207, "Ma'lumotlar kommunikatsiyasi (m)",         'KI23-03', 'juma', 4),
    ('Nazarov',    108, "O'rnatilgan tizimlar (a)",                 'KI23-03', 'juma', 5),

    # ── KI23-04 ──
    ('Toshboyev',  102, 'Individual loyiha',                        'KI23-04', 'dushanba', 4),
    ('Toshboyev',  202, 'Individual loyiha',                        'KI23-04', 'dushanba', 6),
    ('Davronov',     1, 'Hayot faoliyati xavfsizligi/Metrologiya',  'KI23-04', 'seshanba', 5),
    ('Rajabov_J',    1, 'Hayot faoliyati xavfsizligi/Metrologiya',  'KI23-04', 'seshanba', 5),
    ('Mamaraufov', 207, 'Multiagent tizimlar (a)',                  'KI23-04', 'payshanba', 3),
    ('Mirsaidov',  103, "O'rnatilgan tizimlar (a)",                 'KI23-04', 'juma', 5),

    # ── ATS23-06 ──
    ('Abduvaitov', 307, 'SQL da dasturlash (m)',                    'ATS23-06', 'dushanba', 4),
    ('Umarov_E',   307, 'Individual loyiha',                        'ATS23-06', 'dushanba', 5),
    ('Mirsaidov',  302, "O'rnatilgan tizimlar (a)",                 'ATS23-06', 'seshanba', 4),
    ('Isroilov',   204, "O'rnatilgan tizimlar (m)",                 'ATS23-06', 'seshanba', 5),
    ('Umarov_E',   305, 'SQL da dasturlash (a)',                    'ATS23-06', 'chorshanba', 4),
    ('Umarov_E',   204, 'Individual loyiha',                        'ATS23-06', 'chorshanba', 5),
    ('Nurmanova',    1, 'Hayot faoliyati xavfsizligi/Metrologiya',  'ATS23-06', 'payshanba', 4),
    ('Dustmurodov',  2, 'Hayot faoliyati xavfsizligi/Metrologiya',  'ATS23-06', 'payshanba', 4),
    ('Umarov_E',   307, "Ma'lumotlar bazasini boshqarish (a)",      'ATS23-06', 'juma', 3),
    ('Umarov_E',   301, "Ma'lumotlar bazasini boshqarish (m)",      'ATS23-06', 'juma', 4),

    # ── ATS23-07 ──
    ('Bobobekova', 308, 'Raqamli texnologiyalar (a)',               'ATS23-07', 'dushanba', 4),
    ('Kudratov',   302, 'Individual loyiha',                        'ATS23-07', 'chorshanba', 3),
    ('Xaqberdiyev',302, "O'rnatilgan tizimlar (a)",                 'ATS23-07', 'chorshanba', 4),
    ('Bobobekova', 307, "Ma'lumotlar bazasini boshqarish (a)",      'ATS23-07', 'juma', 3),
    ('Kudratov',   202, 'Individual loyiha',                        'ATS23-07', 'juma', 5),

    # ── MT23-10 ──
    ('Raximov_R',  220, 'Kompyuter animatsiyasi (m)',               'MT23-10', 'dushanba', 4),
    ('Xaqberdiyev',314, 'UX dizayn (m)',                            'MT23-10', 'dushanba', 5),
    ('Ibroximova', 305, 'OGMR (m)',                                 'MT23-10', 'dushanba', 5),
    ('Xaqberdiyev',316, 'UX dizayn (m)',                            'MT23-10', 'seshanba', 3),
    ('Ibroximova', 101, 'OGMR (m)',                                 'MT23-10', 'seshanba', 3),
    ('Davronov',     2, 'Hayot faoliyati xavfsizligi/Metrologiya',  'MT23-10', 'seshanba', 4),
    ('Dustmurodov',  3, 'Hayot faoliyati xavfsizligi/Metrologiya',  'MT23-10', 'seshanba', 4),
    ('Raximov_R',  308, 'Kompyuter animatsiyasi (a)',               'MT23-10', 'chorshanba', 4),
    ('Xaqberdiyev',305, 'Individual loyiha',                        'MT23-10', 'chorshanba', 5),
    ('Saidqulov',  308, "O'rnatilgan tizimlar (a)",                 'MT23-10', 'payshanba', 3),
    ('Saidqulov',  307, "O'rnatilgan tizimlar (m)",                 'MT23-10', 'payshanba', 5),
    ('Xaqberdiyev',305, 'Individual loyiha',                        'MT23-10', 'juma', 4),
    ('Xaqberdiyev',104, 'UX dizayn (a)',                            'MT23-10', 'juma', 5),
    ('Ibroximova', 100, 'OGMR (a)',                                 'MT23-10', 'juma', 5),

    # ── SI23-18 ──
    ('Primova',      3, 'Machine learning (a)',                     'SI23-18', 'dushanba', 3),
    ('Primova',    308, 'Machine learning (m)',                     'SI23-18', 'dushanba', 4),
    ('Saidqulov',  307, 'IoT tizimlar va ilovalar (a)',             'SI23-18', 'chorshanba', 4),
    ('Saidqulov',  308, 'IoT tizimlar va ilovalar (m)',             'SI23-18', 'chorshanba', 5),
    ('Umarov_E',   220, "O'rnatilgan tizimlar (a)",                 'SI23-18', 'payshanba', 4),
    ('Saidqulov',  307, "O'rnatilgan tizimlar (m)",                 'SI23-18', 'payshanba', 5),
    ('Ismoilov_I', 302, 'Individual loyiha',                        'SI23-18', 'juma', 4),
    ('Ismoilov_I', 308, 'Individual loyiha',                        'SI23-18', 'juma', 5),

    # ── DI23-13 ──
    ('Qayumov',    201, 'Individual loyiha',                        'DI23-13', 'dushanba', 4),
    ('Shokirov_F', 108, 'MIICH (a)',                                'DI23-13', 'dushanba', 5),
    ('Shokirov_F', 301, 'Mobil ilovalar (m)',                       'DI23-13', 'seshanba', 4),
    ('Mamayev',    214, 'Individual loyiha',                        'DI23-13', 'seshanba', 5),
    ('Mamayev',    219, "DT sifatini ta'minlash (m)",               'DI23-13', 'chorshanba', 4),
    ('Qayumov',    214, 'DT arxitekturasi (a)',                     'DI23-13', 'chorshanba', 5),
    ('Nurmanova',    1, 'Hayot faoliyati xavfsizligi',              'DI23-13', 'payshanba', 4),
    ('Dustmurodov',  2, 'Hayot faoliyati xavfsizligi',              'DI23-13', 'payshanba', 4),
    ('Tursunov',   219, 'DT arxitekturasi (m)',                     'DI23-13', 'payshanba', 5),
    ('Murodov',    219, 'Sonli usullar (m)',                        'DI23-13', 'payshanba', 5),
    ('Shokirov_F',   1, 'Mobil ilovalar (m)',                       'DI23-13', 'juma', 4),
    ('Mamayev',    214, 'DTST (a)',                                  'DI23-13', 'juma', 5),

    # ── DI23-14 ──
    ("To'xtayeva", 215, 'Individual loyiha',                        'DI23-14', 'dushanba', 3),
    ("To'xtayeva", 218, 'Individual loyiha',                        'DI23-14', 'dushanba', 5),
    ('Shokirov_F', 312, 'MIICH (a)',                                'DI23-14', 'seshanba', 5),
    ('Mamayev',    202, 'DTST (a)',                                  'DI23-14', 'chorshanba', 5),
    ('Murodov',    204, 'Sonli usullar (a)',                        'DI23-14', 'juma', 3),

    # ── DI23-15 ──
    ('Ubaydullayev',302,'Individual loyiha',                        'DI23-15', 'dushanba', 4),
    ('Qayumov',    214, 'DT arxitekturasi (a)',                     'DI23-15', 'dushanba', 5),
    ('Bobonazarov',220, 'Sonli usullar (a)',                        'DI23-15', 'dushanba', 5),
    ('Yuldoshev',  220, 'MIICH (a)',                                 'DI23-15', 'seshanba', 5),
    ('Ubaydullayev',220,'Individual loyiha',                        'DI23-15', 'chorshanba', 5),
    ('Tursunov',   215, 'DTST (a)',                                  'DI23-15', 'juma', 5),

    # ── KI23-05 (rus) ──
    ('Abdiyeva',   103, 'Multiagent tizimlar (a)',                  'KI23-05', 'seshanba', 4),
    ('Abdiyeva',   201, 'Multiagent tizimlar (m)',                  'KI23-05', 'seshanba', 5),
    ('Erkinov',    104, 'Individual loyiha',                        'KI23-05', 'payshanba', 3),
    ('Abatov',     302, "O'rnatilgan tizimlar (a)",                 'KI23-05', 'payshanba', 5),
    ('Erkinov',    314, 'Individual loyiha',                        'KI23-05', 'juma', 3),
    ('Abatov',     308, "O'rnatilgan tizimlar (m)",                 'KI23-05', 'juma', 4),

    # ── ATS23-09 (rus) ──
    ('Fattayeva',  305, 'MB ni boshqarish (m)',                     'ATS23-09', 'dushanba', 4),
    ('Kurbaniyozov',307,"O'rnatilgan tizimlar (a)",                 'ATS23-09', 'seshanba', 4),
    ('Fattayeva',  302, 'Individual loyiha',                        'ATS23-09', 'seshanba', 5),
    ('Narmuradov', 102, 'Raqamli texnologiyalar (m)',               'ATS23-09', 'payshanba', 4),
    ('Narmuradov', 102, 'Raqamli texnologiyalar (a)',               'ATS23-09', 'payshanba', 5),
    ('Fattayeva',  305, 'MBni boshqarish (a)',                      'ATS23-09', 'juma', 3),
    ('Abatov',     308, "O'rnatilgan tizimlar (m)",                 'ATS23-09', 'juma', 4),
    ('Narmuradov', 102, 'Raqamli texnologiyalar (m)',               'ATS23-09', 'juma', 5),

    # ── MT23-12 (rus) ──
    ('Abatov',     202, 'Individual loyiha',                        'MT23-12', 'dushanba', 4),
    ('Fattayeva',  104, 'Kompyuter animatsiyasi (a)',               'MT23-12', 'dushanba', 5),
    ('Fattayeva',    3, 'UX dizayn (a)',                            'MT23-12', 'seshanba', 3),
    ('Abatov',     313, 'Individual loyiha',                        'MT23-12', 'seshanba', 4),
    ('Fattayeva',  317, 'UX dizayn (m)',                            'MT23-12', 'payshanba', 3),
    ('Kurbaniyozov',108,"O'rnatilgan tizimlar (a)",                 'MT23-12', 'payshanba', 4),
    ('Abatov',     313, 'IoT tizimlar va ilovalar (m)',             'MT23-12', 'payshanba', 4),
    ('Abatov',     308, "O'rnatilgan tizimlar (m)",                 'MT23-12', 'juma', 4),
    ('Fattayeva',  316, 'Kompyuter animatsiyasi (m)',               'MT23-12', 'juma', 5),

    # ── SI23-19 (rus) ──
    ('Maxmudov_Z', 314, 'Individual loyiha',                        'SI23-19', 'dushanba', 4),
    ('Maxmudov_Z', 316, 'Individual loyiha',                        'SI23-19', 'dushanba', 5),
    ('Buriboyev',  307, 'Machine learning (a)',                     'SI23-19', 'seshanba', 3),
    ('Buriboyev',  307, 'Machine learning (m)',                     'SI23-19', 'seshanba', 4),
    ('Abatov',     313, 'IoT tizimlar va ilovalar (m)',             'SI23-19', 'payshanba', 4),
    ('Umarov_E',   305, "O'rnatilgan tizimlar (a)",                 'SI23-19', 'payshanba', 5),
    ('Abatov',     308, 'IoT tizimlar va ilovalar (a)',             'SI23-19', 'juma', 3),
    ('Safarova',   214, 'DT arxitekturasi (a)',                     'SI23-19', 'juma', 4),

    # ── DI23-17 (rus) ──
    ('Badalova',   104, 'DTST (a)',                                  'DI23-17', 'dushanba', 4),
    ('Badalova',   116, 'DTST (m)',                                  'DI23-17', 'dushanba', 5),
    ('Axmedjanova',102, 'MIICH (a)',                                'DI23-17', 'seshanba', 4),
    ('Axmedjanova',102, 'MIICH (m)',                                'DI23-17', 'seshanba', 5),
    ('Safarova',   214, 'DT arxitekturasi (m)',                     'DI23-17', 'payshanba', 4),

    # ══════════════════════════════════
    # 1-KURS  2-SEMESTR
    # ══════════════════════════════════

    # ── KI25-01 ──
    ('Samadov',    102, 'Dinshunoslik (s)',                         'KI25-01', 'dushanba', 1),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'KI25-01', 'dushanba', 2),
    ('Akromova',   101, 'Xorijiy til 1 (a)',                       'KI25-01', 'dushanba', 2),
    ('Ibatova',      4, 'Xorijiy til 1 (a)',                       'KI25-01', 'dushanba', 2),
    ("Yaxshibo'yev",317,'Hisob (Calculus) 2 (m)',                  'KI25-01', 'dushanba', 3),
    ('Boboqambarova',314,'Fizika 2 (a)',                           'KI25-01', 'dushanba', 4),
    ('Raxmatova',  108, 'Akademik yozuv',                          'KI25-01', 'seshanba', 2),
    ('Qarshiyev',  218, 'Dasturlash 2 (m)',                        'KI25-01', 'seshanba', 3),
    ('Isroilov',   218, 'MTA (m)',                                  'KI25-01', 'seshanba', 3),
    ('Asrorov',    317, 'Fizika 2 (m)',                            'KI25-01', 'chorshanba', 1),
    ('Qarshiyev',  214, 'Dasturlash 2 (a)',                        'KI25-01', 'chorshanba', 2),
    ('Qarshiyev',  218, 'Dasturlash 2 (m)',                        'KI25-01', 'chorshanba', 3),
    ('Isroilov',   218, 'MTA (m)',                                  'KI25-01', 'chorshanba', 3),
    ('Toshpulatov',102, 'Xorijiy til 1 (a)',                       'KI25-01', 'chorshanba', 4),
    ('Akromova',   108, 'Xorijiy til 1 (a)',                       'KI25-01', 'chorshanba', 4),
    ('Ibatova',    104, 'Xorijiy til 1 (a)',                       'KI25-01', 'chorshanba', 4),
    ('Samadov',    103, 'Dinshunoslik (m)',                        'KI25-01', 'payshanba', 1),
    ('Raxmatova',  108, 'Akademik yozuv',                          'KI25-01', 'payshanba', 2),
    ('Kudratov',   202, 'MTA (a)',                                  'KI25-01', 'juma', 1),
    ('Boymurodov', 312, 'Hisob (Calculus) 2 (a)',                  'KI25-01', 'juma', 2),

    # ── KI25-02 ──
    ('Toyirova',   116, 'Akademik yozuv',                          'KI25-02', 'dushanba', 1),
    ('Toyirova',   116, 'Akademik yozuv',                          'KI25-02', 'seshanba', 2),
    ('Juraqulov',  312, 'Hisob (Calculus) 2 (a)',                  'KI25-02', 'juma', 1),
    ('Kudratov',   202, 'MTA (a)',                                  'KI25-02', 'juma', 2),
    ('Rajabov_J',  317, 'Fizika 2 (a)',                            'KI25-02', 'juma', 3),

    # ── KI25-03 ──
    ('Murodov',    301, 'Dasturlash 2 (m)',                        'KI25-03', 'dushanba', 1),
    ('Ibroximova', 301, 'MTA (m)',                                  'KI25-03', 'dushanba', 1),
    ('Urolov',     312, 'Hisob (Calculus) 2 (a)',                  'KI25-03', 'dushanba', 2),
    ('Toyirova',   116, 'Akademik yozuv',                          'KI25-03', 'dushanba', 3),
    ('Kabilova',   101, 'Xorijiy til 1 (a)',                       'KI25-03', 'dushanba', 4),
    ('Narziyeva',    4, 'Xorijiy til 1 (a)',                       'KI25-03', 'dushanba', 4),
    ('Ibatova',      3, 'Xorijiy til 1 (a)',                       'KI25-03', 'dushanba', 4),
    ('Akromova',   103, 'Xorijiy til 1 (a)',                       'KI25-03', 'dushanba', 4),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'KI25-03', 'dushanba', 4),
    ("Yaxshibo'yev",301,'Hisob (Calculus) 2 (m)',                  'KI25-03', 'seshanba', 2),
    ('Rajabov_J',  102, 'Fizika 2 (a)',                            'KI25-03', 'seshanba', 3),
    ('Kabilova',   104, 'Xorijiy til 1 (a)',                       'KI25-03', 'chorshanba', 1),
    ('Narziyeva',    4, 'Xorijiy til 1 (a)',                       'KI25-03', 'chorshanba', 1),
    ('Ibatova',      3, 'Xorijiy til 1 (a)',                       'KI25-03', 'chorshanba', 1),
    ('Akromova',   102, 'Xorijiy til 1 (a)',                       'KI25-03', 'chorshanba', 1),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'KI25-03', 'chorshanba', 1),
    ('Toyirova',   116, 'Akademik yozuv',                          'KI25-03', 'chorshanba', 2),
    ('Xaqberdiyev',301, 'MTA (a)',                                  'KI25-03', 'chorshanba', 2),
    ("Yaxshibo'yev",301,'Hisob (Calculus) 2 (m)',                  'KI25-03', 'chorshanba', 3),
    ('Azimov',     301, 'Fizika 2 (m)',                            'KI25-03', 'payshanba', 1),
    ('Murodov',    214, 'Dasturlash 2 (a)',                        'KI25-03', 'payshanba', 2),
    ('Murodov',    301, 'Dasturlash 2 (m)',                        'KI25-03', 'payshanba', 3),
    ('Ibroximova', 301, 'MTA (m)',                                  'KI25-03', 'payshanba', 3),
    ('Kubayeva_Sh',301, 'Dinshunoslik (m)',                        'KI25-03', 'juma', 1),
    ('Xaqberdiyev',201, 'MTA (a)',                                  'KI25-03', 'juma', 2),

    # ── KI25-04 ──
    ('Rajabov_J',  314, 'Fizika 2 (a)',                            'KI25-04', 'dushanba', 3),
    ('Kabilova',   101, 'Xorijiy til 1 (a)',                       'KI25-04', 'dushanba', 4),
    ('Narziyeva',    4, 'Xorijiy til 1 (a)',                       'KI25-04', 'dushanba', 4),
    ('Ibatova',      3, 'Xorijiy til 1 (a)',                       'KI25-04', 'dushanba', 4),
    ('Akromova',   103, 'Xorijiy til 1 (a)',                       'KI25-04', 'dushanba', 4),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'KI25-04', 'dushanba', 4),
    ('Toyirova',   116, 'Akademik yozuv',                          'KI25-04', 'seshanba', 1),
    ('Toyirova',   116, 'Akademik yozuv',                          'KI25-04', 'seshanba', 4),
    ('Xaqberdiyev',301, 'MTA (a)',                                  'KI25-04', 'chorshanba', 2),
    ('Juraqulov',  312, 'Hisob (Calculus) 2 (a)',                  'KI25-04', 'chorshanba', 2),
    ('Mirsaidov',  302, 'Dasturlash 2 (a)',                        'KI25-04', 'payshanba', 2),
    ('Kubayeva_Sh',103, 'Dinshunoslik (s)',                        'KI25-04', 'juma', 2),
    ('Boymurodov', 312, 'Hisob (Calculus) 2 (a)',                  'KI25-04', 'juma', 3),

    # ── KI25-05 ──
    ('Rajabov_J',  103, 'Fizika 2 (a)',                            'KI25-05', 'dushanba', 2),
    ("Yaxshibo'yev",301,'Hisob (Calculus) 2 (m)',                  'KI25-05', 'seshanba', 2),
    ('Kubayeva_Sh',308, 'Dinshunoslik (s)',                        'KI25-05', 'payshanba', 2),
    ('Mirsaidov',  214, 'MTA (a)',                                  'KI25-05', 'juma', 2),
    ('Kubayeva_Sh',102, 'Dinshunoslik (s)',                        'KI25-05', 'juma', 3),
    ('Obloqulov',  214, 'Dasturlash 2 (a)',                        'KI25-05', 'juma', 3),

    # ── DI25-07 ──
    ('Raxmatova',  108, 'Akademik yozuv',                          'DI25-07', 'dushanba', 1),
    ('Boynazarov', 218, 'Dasturlash 2 (m)',                        'DI25-07', 'dushanba', 2),
    ('Ibroximova', 218, 'MTA (m)',                                  'DI25-07', 'dushanba', 2),
    ('Samadov',    103, 'Dinshunoslik (m)',                        'DI25-07', 'dushanba', 3),
    ('Boynazarov', 214, 'Dasturlash 2 (a)',                        'DI25-07', 'dushanba', 4),
    ('Samadov',    102, 'Dinshunoslik (s)',                        'DI25-07', 'seshanba', 1),
    ('Azimov',     314, 'Fizika 2 (a)',                            'DI25-07', 'seshanba', 2),
    ('Indiaminov', 204, 'Hisob (Calculus) 2 (m)',                  'DI25-07', 'seshanba', 3),
    ('Raxmatova',  108, 'Akademik yozuv',                          'DI25-07', 'chorshanba', 1),
    ('Dustmurodov',317, 'Fizika 2 (m)',                            'DI25-07', 'chorshanba', 2),
    ('Ibroximova', 219, 'MTA (a)',                                  'DI25-07', 'chorshanba', 3),
    ('Boynazarov', 218, 'Dasturlash 2 (m)',                        'DI25-07', 'payshanba', 2),
    ('Indiaminov', 204, 'Hisob (Calculus) 2 (m)',                  'DI25-07', 'payshanba', 3),
    ('Toshpulatov',104, 'Xorijiy til 1 (a)',                       'DI25-07', 'juma', 1),
    ('Ibatova',    101, 'Xorijiy til 1 (a)',                       'DI25-07', 'juma', 1),
    ('Akromova',   103, 'Xorijiy til 1 (a)',                       'DI25-07', 'juma', 1),
    ('Urolov',     313, 'Hisob (Calculus) 2 (a)',                  'DI25-07', 'juma', 2),
    ('Toshpulatov',104, 'Xorijiy til 1 (a)',                       'DI25-07', 'juma', 3),
    ('Ibatova',    101, 'Xorijiy til 1 (a)',                       'DI25-07', 'juma', 3),
    ('Akromova',   116, 'Xorijiy til 1 (a)',                       'DI25-07', 'juma', 3),

    # ── DI25-08 ──
    ('Ubaydullayev',214,'Dasturlash 2 (a)',                        'DI25-08', 'dushanba', 1),
    ('Boynazarov', 218, 'Dasturlash 2 (m)',                        'DI25-08', 'dushanba', 2),
    ('Ibroximova', 218, 'MTA (m)',                                  'DI25-08', 'dushanba', 2),
    ('Azimov',     312, 'Fizika 2 (a)',                            'DI25-08', 'seshanba', 1),
    ('Samadov',    102, 'Dinshunoslik (s)',                        'DI25-08', 'seshanba', 2),
    ('Mirsaidov',  307, 'MTA (a)',                                  'DI25-08', 'payshanba', 1),
    ('Juraqulov',  317, 'Hisob (Calculus) 2 (a)',                  'DI25-08', 'juma', 2),

    # ── DI25-09 ──
    ('Abdiyev_M',    2, 'Akademik yozuv',                          'DI25-09', 'dushanba', 1),
    ('Rajabov_J',    1, 'Fizika 2 (a)',                            'DI25-09', 'dushanba', 1),
    ('Samadov',    102, 'Dinshunoslik (s)',                        'DI25-09', 'dushanba', 2),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'DI25-09', 'dushanba', 3),
    ('Ibatova',    101, 'Xorijiy til 1 (a)',                       'DI25-09', 'dushanba', 3),
    ('Akromova',   100, 'Xorijiy til 1 (a)',                       'DI25-09', 'dushanba', 3),
    ('Xaqberdiyev',116, 'MTA (a)',                                  'DI25-09', 'dushanba', 4),
    ('Abdiyev_M',    2, 'Akademik yozuv',                          'DI25-09', 'seshanba', 1),
    ('Tursunov',   214, 'Dasturlash 2 (a)',                        'DI25-09', 'seshanba', 2),
    ('Samadov',    103, 'Dinshunoslik (m)',                        'DI25-09', 'seshanba', 3),
    ('Juraqulov',  103, 'Hisob (Calculus) 2 (m)',                  'DI25-09', 'chorshanba', 1),
    ('Tursunov',   103, 'Dasturlash 2 (m)',                        'DI25-09', 'chorshanba', 2),
    ('Isroilov',   103, 'MTA (m)',                                  'DI25-09', 'chorshanba', 2),
    ('Asrorov',    103, 'Fizika 2 (m)',                            'DI25-09', 'chorshanba', 3),
    ('Tursunov',   101, 'Dasturlash 2 (m)',                        'DI25-09', 'payshanba', 1),
    ('Isroilov',   101, 'MTA (m)',                                  'DI25-09', 'payshanba', 1),
    ('Azimov',     314, 'Fizika 2 (a)',                            'DI25-09', 'payshanba', 2),
    ('Urolov',     313, 'Hisob (Calculus) 2 (a)',                  'DI25-09', 'juma', 1),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'DI25-09', 'juma', 2),
    ('Ibatova',    104, 'Xorijiy til 1 (a)',                       'DI25-09', 'juma', 2),
    ('Akromova',   116, 'Xorijiy til 1 (a)',                       'DI25-09', 'juma', 2),
    ('Juraqulov',  103, 'Hisob (Calculus) 2 (m)',                  'DI25-09', 'juma', 3),

    # ── DI25-10 ──
    ('Abdiyev_M',    2, 'Akademik yozuv',                          'DI25-10', 'dushanba', 2),
    ('Raximov_R',  103, 'MTA (a)',                                  'DI25-10', 'seshanba', 1),
    ('Abdiyev_M',    2, 'Akademik yozuv',                          'DI25-10', 'seshanba', 2),
    ('Obloqulov',  202, 'Dasturlash 2 (a)',                        'DI25-10', 'payshanba', 2),
    ('Boymurodov',   4, 'Hisob (Calculus) 2 (a)',                  'DI25-10', 'juma', 1),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'DI25-10', 'juma', 2),
    ('Ibatova',    104, 'Xorijiy til 1 (a)',                       'DI25-10', 'juma', 2),
    ('Akromova',   116, 'Xorijiy til 1 (a)',                       'DI25-10', 'juma', 2),

    # ── SI25-12 ──
    ('Akromova',   103, 'Xorijiy til 1 (a)',                       'SI25-12', 'dushanba', 1),
    ('Ibatova',    101, 'Xorijiy til 1 (a)',                       'SI25-12', 'dushanba', 1),
    ('Toshpulatov',  3, 'Xorijiy til 1 (a)',                       'SI25-12', 'dushanba', 1),
    ('Narziyeva',    4, 'Xorijiy til 1 (a)',                       'SI25-12', 'dushanba', 1),
    ('Absalomov',    1, 'Hisob (Calculus) 2 (m)',                  'SI25-12', 'dushanba', 2),
    ('Boboqambarova',1, 'Fizika 2 (m)',                            'SI25-12', 'dushanba', 3),
    ('Diyorov',    317, 'Hisob (Calculus) 2 (a)',                  'SI25-12', 'seshanba', 1),
    ('Boynazarov', 103, 'Dasturlash 2 (m)',                        'SI25-12', 'seshanba', 2),
    ('Buriboyev',  103, 'MTA (m)',                                  'SI25-12', 'seshanba', 2),
    ('Raximov_R',    3, 'MTA (a)',                                  'SI25-12', 'seshanba', 3),
    ('Boynazarov', 101, 'Dasturlash 2 (m)',                        'SI25-12', 'chorshanba', 1),
    ('Buriboyev',  101, 'MTA (m)',                                  'SI25-12', 'chorshanba', 1),
    ('Raxmatova',  108, 'Akademik yozuv',                          'SI25-12', 'chorshanba', 2),
    ('Akromova',   100, 'Xorijiy til 1 (a)',                       'SI25-12', 'chorshanba', 3),
    ('Ibatova',    101, 'Xorijiy til 1 (a)',                       'SI25-12', 'chorshanba', 3),
    ('Toshpulatov',  4, 'Xorijiy til 1 (a)',                       'SI25-12', 'chorshanba', 3),
    ('Narziyeva',    3, 'Xorijiy til 1 (a)',                       'SI25-12', 'chorshanba', 3),

    # ── SI25-13 ──
    ("To'xtayeva", 108, 'Dasturlash 2 (a)',                        'SI25-13', 'dushanba', 4),
    ('Xaqberdiyev',101, 'MTA (a)',                                  'SI25-13', 'seshanba', 1),
    ('Raxmatova',  108, 'Akademik yozuv',                          'SI25-13', 'seshanba', 3),
    ('Urolov',       1, 'Hisob (Calculus) 2 (a)',                  'SI25-13', 'chorshanba', 2),

    # ── KI25-06 (rus) ──
    ('Ishonkulov', 313, 'Hisob (Calculus) 2 (m)',                  'KI25-06', 'dushanba', 1),
    ('Raxmatova',  108, 'Akademik yozuv',                          'KI25-06', 'dushanba', 2),
    ('Djumayozov', 313, 'Dasturlash 2 (m)',                        'KI25-06', 'dushanba', 3),
    ('Maxmudov_Z', 313, 'MTA (m)',                                  'KI25-06', 'dushanba', 3),
    ('Rizoyev',    313, 'Dinshunoslik (m)',                        'KI25-06', 'seshanba', 2),
    ('Diyorov',    314, 'Hisob (Calculus) 2 (a)',                  'KI25-06', 'seshanba', 3),
    ('Rizoyev',    104, 'Dinshunoslik (s)',                        'KI25-06', 'seshanba', 4),
    ('Djumayozov', 313, 'Dasturlash 2 (m)',                        'KI25-06', 'chorshanba', 1),
    ('Maxmudov_Z', 313, 'MTA (m)',                                  'KI25-06', 'chorshanba', 1),
    ('Ibatova',    101, 'Xorijiy til 1 (a)',                       'KI25-06', 'chorshanba', 2),
    ('Toshpulatov',  4, 'Xorijiy til 1 (a)',                       'KI25-06', 'chorshanba', 2),
    ('Narziyeva',    3, 'Xorijiy til 1 (a)',                       'KI25-06', 'chorshanba', 2),
    ('Akromova',   102, 'Xorijiy til 1 (a)',                       'KI25-06', 'chorshanba', 2),
    ('Djumayozov', 214, 'Dasturlash 2 (a)',                        'KI25-06', 'chorshanba', 3),
    ('Raxmatova',  108, 'Akademik yozuv',                          'KI25-06', 'payshanba', 1),
    ('Ishonkulov', 314, 'Hisob (Calculus) 2 (a)',                  'KI25-06', 'payshanba', 1),
    ('Ishonkulov', 313, 'Hisob (Calculus) 2 (m)',                  'KI25-06', 'payshanba', 2),
    ('Maxmudov_Z', 302, 'MTA (a)',                                  'KI25-06', 'juma', 1),
    ('Asrorov',    314, 'Fizika 2 (a)',                            'KI25-06', 'juma', 2),
    ('Asrorov',    313, 'Fizika 2 (m)',                            'KI25-06', 'juma', 3),
    ('Ibatova',    104, 'Xorijiy til 1 (a)',                       'KI25-06', 'juma', 4),
    ('Toshpulatov',316, 'Xorijiy til 1 (a)',                       'KI25-06', 'juma', 4),
    ('Narziyeva',  102, 'Xorijiy til 1 (a)',                       'KI25-06', 'juma', 4),
    ('Akromova',   108, 'Xorijiy til 1 (a)',                       'KI25-06', 'juma', 4),

    # ── DI25-11 (rus) ──
    ('Djumayozov', 214, 'Dasturlash 2 (a)',                        'DI25-11', 'dushanba', 2),
    ('Raxmatova',  108, 'Akademik yozuv',                          'DI25-11', 'seshanba', 1),
    ('Rizoyev',    104, 'Dinshunoslik (s)',                        'DI25-11', 'seshanba', 3),
    ('Raxmatova',  108, 'Akademik yozuv',                          'DI25-11', 'chorshanba', 3),
    ('Maxmudov_Z', 302, 'MTA (a)',                                  'DI25-11', 'chorshanba', 2),
    ('Ishonkulov', 314, 'Hisob (Calculus) 2 (a)',                  'DI25-11', 'payshanba', 1),
    ('Asrorov',    314, 'Fizika 2 (a)',                            'DI25-11', 'juma', 1),
    ('Maxmudov_Z', 302, 'MTA (a)',                                  'DI25-11', 'juma', 2),

    # ── SI25-14 (rus) ──
    ('Asrorov',    314, 'Fizika 2 (a)',                            'SI25-14', 'dushanba', 2),
    ("Yaxshibo'yev",317,'Hisob (Calculus) 2 (a)',                  'SI25-14', 'seshanba', 3),
    ('Maxmudov_Z', 201, 'MTA (a)',                                  'SI25-14', 'seshanba', 4),
    ('Raxmatova',  108, 'Akademik yozuv',                          'SI25-14', 'payshanba', 3),
    ('Ubaydullayev',214,'Dasturlash 2 (a)',                        'SI25-14', 'juma', 1),
    ('Raxmatova',  108, 'Akademik yozuv',                          'SI25-14', 'juma', 2),
]

# familiya_lookup → actual DB familiya mapping (agar farq bo'lsa)
FAMILIYA_MAP = {
    'Umarov_E':    'Umarov',      # kafedra_id=5 Umarov E. (id=65), not id=112
    'Rajabov_J':   'Rajabov',     # kafedra_id=4 Rajabov J. (id=33), not kafedra_id=3 O.
    'Raximov_R':   'Raximov',     # kafedra_id=5 (id=55), not kafedra_id=8 Alisher
    'Shokirov_F':  'Shokirov',    # kafedra_id=9 (id=121)
    'Ismoilov_I':  'Ismoilov',    # kafedra_id=5 (id=137)
    'Maxmudov_Z':  'Maxmudov',    # kafedra_id=5 (id=52)
    'Abdiyev_M':   'Abdiyev',     # kafedra_id=1 (id=146)
    'Kubayeva_Sh': 'Kubayeva',    # Sh. (id=10), not G.E.
    "Yaxshibo'yev":"Yaxshibo'yev",
    'Samadov':     'Samadov',
    'Toyirova':    'Toyirova',
}

# familiya → (kafedra_id, id) belgilovchi qo'shimcha filter
FAMILIYA_KAFEDRA = {
    'Umarov_E':    5,   # Axborot texnologiyalari
    'Rajabov_J':   4,   # Tabiiy fanlar
    'Raximov_R':   5,   # Axborot texnologiyalari
    'Shokirov_F':  9,   # Raqamli
    'Ismoilov_I':  5,   # Axborot texnologiyalari
    'Maxmudov_Z':  5,   # Axborot texnologiyalari
    'Abdiyev_M':   1,   # Tillar
    'Kubayeva_Sh': 2,   # Ijtimoiy gumanitar-1
    'Yuldoshev':   9,   # Raqamli
    'Azimov':      4,   # Tabiiy fanlar (id=31)
}


async def main():
    conn = await asyncpg.connect(DB_DSN)
    try:
        # ── 0. Eski B-bino ma'lumotlarni tozalash ────────────────────────────
        await conn.execute("DELETE FROM dars_jadvali WHERE bino='B'")
        await conn.execute("DELETE FROM xonalar WHERE bino='B'")
        print("✅ Eski B-bino ma'lumotlar o'chirildi")

        # ── 1. Xonalar ────────────────────────────────────────────────────────
        await conn.executemany(
            "INSERT INTO xonalar (raqam, bino, qavat) VALUES ($1, 'B', $2)",
            B_XONALAR
        )
        print(f"✅ {len(B_XONALAR)} ta B-bino xona qo'shildi")

        # ── 2. Yangi o'qituvchilar ─────────────────────────────────────────────
        inserted = 0
        for kafedra_nomi, familiya, ism in YANGI_OQITUVCHILAR:
            exists = await conn.fetchval(
                "SELECT id FROM oqituvchilar WHERE familiya=$1 LIMIT 1", familiya
            )
            if not exists:
                await conn.execute(
                    """INSERT INTO oqituvchilar (kafedra_id, familiya, ism, bino, faol)
                       SELECT id, $2, $3, 'B', TRUE FROM kafedralar WHERE nomi=$1""",
                    kafedra_nomi, familiya, ism
                )
                inserted += 1
        print(f"✅ {inserted} ta yangi o'qituvchi qo'shildi")

        # ── 3. O'qituvchilar ID lari lug'ati ──────────────────────────────────
        rows = await conn.fetch(
            "SELECT id, familiya, kafedra_id FROM oqituvchilar WHERE faol=TRUE"
        )
        # familiya → id (default first match)
        fam_to_id: dict[str, int] = {}
        # kafedra-specific: (familiya, kafedra_id) → id
        fam_kafedra_to_id: dict[tuple, int] = {}
        for r in rows:
            fam = r['familiya']
            kid = r['kafedra_id']
            oid = r['id']
            if fam not in fam_to_id:
                fam_to_id[fam] = oid
            fam_kafedra_to_id[(fam, kid)] = oid

        def lookup(lookup_key: str) -> int | None:
            real_fam = FAMILIYA_MAP.get(lookup_key, lookup_key)
            k_id = FAMILIYA_KAFEDRA.get(lookup_key)
            if k_id:
                result = fam_kafedra_to_id.get((real_fam, k_id))
                if result:
                    return result
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
            dars_rows.append((oid, xona, 'B', fan, guruh, kun, bosh, tug))

        if not_found:
            print(f"⚠️  Topilmagan o'qituvchilar: {not_found}")

        await conn.executemany(
            """INSERT INTO dars_jadvali
               (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
            dars_rows
        )
        print(f"✅ {len(dars_rows)} ta dars jadvali yozuvi qo'shildi")

        # ── 5. Tekshirish ─────────────────────────────────────────────────────
        xona_cnt = await conn.fetchval("SELECT COUNT(*) FROM xonalar WHERE bino='B'")
        dars_cnt = await conn.fetchval("SELECT COUNT(*) FROM dars_jadvali WHERE bino='B'")
        print(f"\n📊 Natija:")
        print(f"   B-bino xonalar: {xona_cnt}")
        print(f"   B-bino darslar: {dars_cnt}")

        top = await conn.fetch(
            """SELECT o.familiya, COUNT(d.id) AS soni
               FROM dars_jadvali d
               JOIN oqituvchilar o ON o.id=d.oqituvchi_id
               WHERE d.bino='B'
               GROUP BY o.familiya
               ORDER BY soni DESC LIMIT 15"""
        )
        print("\n🏆 Ko'p dars beradiganlar (top-15):")
        for r in top:
            print(f"   {r['familiya']:20s} {r['soni']} ta")

    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
