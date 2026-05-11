import asyncio
import asyncpg
from datetime import time as dtime
from config import DB_DSN


def t(s: str) -> dtime:
    h, m = map(int, s.split(':'))
    return dtime(h, m)

# ─── O'qituvchi nomi → familiya ILIKE pattern ────────────────────
INSERTS = [
    # ── SESHANBA ─────────────────────────────────────────────────
    # AKT23-01 | 5-juft 15:00-16:20
    ("Rajabov%",      201, "Moliyaviy savodxonlik",                  "AKT23-01", "seshanba",   t("15:00"), t("16:20")),
    ("Usmonov%",      331, "Pedagogika",                             "AKT23-01", "seshanba",   t("15:00"), t("16:20")),
    ("Fozilov%",      314, "Atrof-muhit",                            "AKT23-01", "seshanba",   t("15:00"), t("16:20")),

    # ── CHORSHANBA ───────────────────────────────────────────────
    # AKT23-01 | 4-juft
    ("Muhammadiyev%", 127, "Kreativ pedagogika/STEAM ta'lim",        "AKT23-01", "chorshanba", t("13:30"), t("14:50")),
    ("Yo%ldoshev%",   226, "Kreativ pedagogika/STEAM ta'lim",        "AKT23-01", "chorshanba", t("13:30"), t("14:50")),
    # AX23-08 | 4-juft
    ("Nishonova%",    214, "Stenografik algoritmlar",                "AX23-08",  "chorshanba", t("13:30"), t("14:50")),
    # RI23-10 | 4-juft
    ("Togayeva%",     112, "Soliq va soliqqa tortish",               "RI23-10",  "chorshanba", t("13:30"), t("14:50")),
    # AKT23-01 | 5-juft
    ("Shodmonov%",    321, "Raqamli texnologiya va innovatsiyalar",  "AKT23-01", "chorshanba", t("15:00"), t("16:20")),
    # AX23-12 | 5-juft
    ("Nishonova%",    314, "Tarmoq xavfsizligi",                     "AX23-12",  "chorshanba", t("15:00"), t("16:20")),
    # RI23-10 | 5-juft
    ("Baxodirov%",    217, "Raqamli iqtisodiyot va innovatsiya",     "RI23-10",  "chorshanba", t("15:00"), t("16:20")),

    # ── PAYSHANBA ────────────────────────────────────────────────
    # AX23-08 | 1-juft
    ("Kiyamov%",      304, "Individual loyiha",                      "AX23-08",  "payshanba",  t("08:30"), t("09:50")),
    # AKT23-01 | 2-juft
    ("Ismoilov%",     227, "O'rnatilgan tizimlar",                   "AKT23-01", "payshanba",  t("10:00"), t("11:20")),
    # AX23-12 | 2-juft
    ("Baxodirov%",    112, "Individual loyiha",                      "AX23-12",  "payshanba",  t("10:00"), t("11:20")),
    # AKT23-01 | 3-juft
    ("Ismoilov%",     227, "O'rnatilgan tizimlar",                   "AKT23-01", "payshanba",  t("11:30"), t("12:50")),
    # AX23-12 | 3-juft
    ("Baxodirov%",    217, "Raqamli iqtisodiyot va innovatsiya",     "AX23-12",  "payshanba",  t("11:30"), t("12:50")),
    # AKT23-01 | 4-juft
    ("Ismoilov%",     317, "O'rnatilgan tizimlar",                   "AKT23-01", "payshanba",  t("13:30"), t("14:50")),
    # AX23-08 | 4-juft
    ("Haqberdiyev%",  127, "O'rnatilgan tizimlar",                   "AX23-08",  "payshanba",  t("13:30"), t("14:50")),
    # AX23-12 | 4-juft
    ("Shakarov%",     112, "Individual loyiha",                      "AX23-12",  "payshanba",  t("13:30"), t("14:50")),
    # RI23-10 | 4-juft — toq hafta
    ("Togayeva%",     201, "Moliya bozori",                          "RI23-10",  "payshanba",  t("13:30"), t("14:50")),
    # RI23-10 | 4-juft — juft hafta
    ("Togayeva%",     201, "Soliq va soliqqa tortish",               "RI23-10",  "payshanba",  t("13:30"), t("14:50")),
    # AKT23-01 | 5-juft — juft hafta
    ("Shodmonov%",    321, "Raqamli texnologiya va innovatsiyalar",  "AKT23-01", "payshanba",  t("15:00"), t("16:20")),
    # AX23-08 | 5-juft
    ("Haqberdiyev%",  304, "O'rnatilgan tizimlar",                   "AX23-08",  "payshanba",  t("15:00"), t("16:20")),
    # RI23-10 | 5-juft
    ("Togayeva%",     331, "Moliya bozori",                          "RI23-10",  "payshanba",  t("15:00"), t("16:20")),

    # ── JUMA ─────────────────────────────────────────────────────
    # AX23-12 | 1-juft
    ("Shakarov%",     304, "Individual loyiha",                      "AX23-12",  "juma",       t("08:30"), t("09:50")),
    # AX23-08 | 2-juft
    ("Kiyamov%",      301, "Individual loyiha",                      "AX23-08",  "juma",       t("10:00"), t("11:20")),
    # AX23-08 | 3-juft
    ("Kiyamov%",      304, "Server Administration",                  "AX23-08",  "juma",       t("11:30"), t("12:50")),
    # AX23-12 | 3-juft
    ("Baxodirov%",    127, "Individual loyiha",                      "AX23-12",  "juma",       t("11:30"), t("12:50")),
    # AKT23-01 | 4-juft
    ("Mamanazarov%",  315, "Kreativ pedagogika/STEAM ta'lim",        "AKT23-01", "juma",       t("13:30"), t("14:50")),
    ("Yo%ldoshev%",   321, "Kreativ pedagogika/STEAM ta'lim",        "AKT23-01", "juma",       t("13:30"), t("14:50")),
    # RI23-10 | 4-juft
    ("Togayeva%",     314, "Soliq va soliqqa tortish",               "RI23-10",  "juma",       t("13:30"), t("14:50")),
    # RI23-10 | 5-juft
    ("Togayeva%",     314, "Moliya bozori",                          "RI23-10",  "juma",       t("15:00"), t("16:20")),
]

SQL = """
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, $2, 'A', $3, $4, $5, $6, $7
FROM oqituvchilar o
WHERE o.familiya ILIKE $1
LIMIT 1
"""

CHECK_SQL = """
SELECT o.familiya, d.guruh, d.kun, d.boshlanish, d.tugash, d.xona_raqam, d.fan_nomi
FROM dars_jadvali d
JOIN oqituvchilar o ON o.id = d.oqituvchi_id
WHERE d.bino = 'A'
  AND d.guruh IN ('AKT23-01','AX23-08','AX23-12','RI23-10')
ORDER BY
  d.guruh,
  CASE d.kun
    WHEN 'dushanba'   THEN 1 WHEN 'seshanba'   THEN 2
    WHEN 'chorshanba' THEN 3 WHEN 'payshanba'  THEN 4
    WHEN 'juma'       THEN 5
  END,
  d.boshlanish
"""


async def main():
    conn = await asyncpg.connect(DB_DSN)

    print("=" * 60)
    print("O'QITUVCHILAR TEKSHIRUVI")
    print("=" * 60)
    teachers = await conn.fetch("SELECT id, familiya, ism FROM oqituvchilar ORDER BY familiya")
    for t in teachers:
        print(f"  {t['id']:3d}  {t['familiya']} {t['ism']}")

    print(f"\n{'=' * 60}")
    print(f"INSERT BOSHLANDI — jami {len(INSERTS)} ta qator")
    print("=" * 60)

    ok = 0
    skipped = 0
    for row in INSERTS:
        familiya_pattern, xona, fan, guruh, kun, bosh, tug = row
        # O'qituvchi mavjudligini oldin tekshiramiz
        teacher = await conn.fetchrow(
            "SELECT id, familiya, ism FROM oqituvchilar WHERE familiya ILIKE $1 LIMIT 1",
            familiya_pattern,
        )
        if not teacher:
            print(f"  [??] TOPILMADI: {familiya_pattern!r} | {guruh} | {kun} {bosh} | {fan}")
            skipped += 1
            continue

        result = await conn.execute(SQL, familiya_pattern, xona, fan, guruh, kun, bosh, tug)  # noqa
        affected = int(result.split()[-1])
        if affected:
            print(f"  [OK]  {teacher['familiya']:<18} | {guruh:<10} | {kun:<12} {bosh}-{tug} | xona {xona} | {fan}")
            ok += 1
        else:
            print(f"  [!!]  0 QATOR: {teacher['familiya']!r} | {guruh} | {kun} {bosh}")
            skipped += 1

    print(f"\n{'=' * 60}")
    print(f"NATIJA: {ok} ta kiritildi, {skipped} ta o'tkazib yuborildi")
    print("=" * 60)

    print(f"\n{'=' * 60}")
    print("TEKSHIRISH — KIRITILGAN JADVAL")
    print("=" * 60)
    rows = await conn.fetch(CHECK_SQL)
    prev_guruh = None
    for r in rows:
        if r['guruh'] != prev_guruh:
            print(f"\n  [{r['guruh']}]")
            prev_guruh = r['guruh']
        bosh = str(r['boshlanish'])[:5]
        tug  = str(r['tugash'])[:5]
        print(f"    {r['kun']:<12} {bosh}–{tug}  xona {r['xona_raqam']}  {r['familiya']:<18}  {r['fan_nomi']}")

    await conn.close()


asyncio.run(main())
