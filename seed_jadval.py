import asyncio
import asyncpg
from datetime import time

DB_DSN = "postgresql://postgres:2304@localhost:5432/tatu_sf"

VAQTLAR = {
    1: (time(8,  30), time(9,  50)),
    2: (time(10,  0), time(11, 20)),
    3: (time(11, 30), time(12, 50)),
    4: (time(13, 30), time(14, 50)),
    5: (time(15,  0), time(16, 20)),
    6: (time(16, 30), time(17, 50)),
}


async def main():
    pool = await asyncpg.create_pool(DB_DSN)
    async with pool.acquire() as conn:

        # ── 1. Bazada yo'q o'qituvchilarni qo'shish ─────────────────────────
        print("=== Yo'q o'qituvchilar qo'shilmoqda ===")
        missing = [
            # (kafedra_id, ism, familiya)
            (6, 'F.',  'Ismoilov'),   # Dasturlash 2  (Boynazarov I. kafedrasida)
            (5, 'I.',  'Ismoilov'),   # O'rnatilgan tizimlar
            (3, 'A.',  'Usmonov'),    # Moliyaviy savodxonlik
            (7, 'A.',  'Xaniyev'),    # Diskret tuzilmalar
        ]
        inserted_ids = {}
        for kafedra_id, ism, familiya in missing:
            key = f"{familiya}_{ism}"
            existing = await conn.fetchrow(
                "SELECT id FROM oqituvchilar WHERE familiya=$1 AND ism=$2",
                familiya, ism
            )
            if existing:
                inserted_ids[key] = existing['id']
                print(f"  Mavjud: {familiya} {ism} -> id={existing['id']}")
            else:
                row = await conn.fetchrow(
                    "INSERT INTO oqituvchilar (kafedra_id, ism, familiya, faol) "
                    "VALUES ($1,$2,$3,TRUE) RETURNING id",
                    kafedra_id, ism, familiya
                )
                inserted_ids[key] = row['id']
                print(f"  Qo'shildi: {familiya} {ism} -> id={row['id']}")

        ismoilov_f = inserted_ids['Ismoilov_F.']
        ismoilov_i = inserted_ids['Ismoilov_I.']
        usmonov_a  = inserted_ids['Usmonov_A.']
        xaniyev_a  = inserted_ids['Xaniyev_A.']

        # ── 2. Xonalar ───────────────────────────────────────────────────────
        print("\n=== Xonalar qo'shilmoqda ===")
        xonalar_list = []
        # A-bino
        for r in list(range(101, 120)) + [127]:
            xonalar_list.append((r, 'A', 1))
        for r in list(range(201, 221)) + list(range(226, 232)):
            xonalar_list.append((r, 'A', 2))
        for r in list(range(301, 322)) + [325, 328, 331]:
            xonalar_list.append((r, 'A', 3))
        # B-bino
        for r in list(range(101, 120)) + [127]:
            xonalar_list.append((r, 'B', 1))
        for r in list(range(201, 221)) + list(range(226, 232)):
            xonalar_list.append((r, 'B', 2))
        for r in list(range(301, 322)):
            xonalar_list.append((r, 'B', 3))

        x_inserted = 0
        for raqam, bino, qavat in xonalar_list:
            exists = await conn.fetchval(
                "SELECT 1 FROM xonalar WHERE raqam=$1 AND bino=$2", raqam, bino
            )
            if not exists:
                await conn.execute(
                    "INSERT INTO xonalar (raqam, bino, qavat) VALUES ($1,$2,$3)",
                    raqam, bino, qavat
                )
                x_inserted += 1
        print(f"  {x_inserted} ta yangi xona, {len(xonalar_list)} ta jami (A+B)")

        # ── 3. Dars jadvali ──────────────────────────────────────────────────
        print("\n=== Dars jadvali qo'shilmoqda ===")

        # (guruh, fan_nomi, oqituvchi_id, bino, xona_raqam, juft, kun)
        jadval = [

            # ════════════════════════════════════════════════════════════════
            # RASM 1 — ATT-25-12, ATT-25-13  (1-kurs, A-bino)
            # ════════════════════════════════════════════════════════════════

            # ─── DUSHANBA ────────────────────────────────────────────────────
            ('ATT-25-13', 'Fizika 2',                           31, 'A', 314, 1, 'dushanba'),
            ('ATT-25-13', 'Hisob (calculus) 2',                 34, 'A', 314, 2, 'dushanba'),
            ('ATT-25-13', 'Dinshunoslik',                       13, 'A', 314, 3, 'dushanba'),

            # ─── SESHANBA ────────────────────────────────────────────────────
            ('ATT-25-12', 'Dinshunoslik',                       13, 'A', 314, 2, 'seshanba'),
            ('ATT-25-13', "O'zbekistonning eng yangi tarixi",    9,  'A', 314, 1, 'seshanba'),
            ('ATT-25-13', "Ma'lumotlar tuzilmasi va algoritmlar",63, 'A', 301, 2, 'seshanba'),
            ('ATT-25-13', 'Dinshunoslik',                       13, 'A', 307, 5, 'seshanba'),

            # ─── CHORSHANBA ──────────────────────────────────────────────────
            ('ATT-25-12', "Ma'lumotlar tuzilmasi va algoritmlar",56, 'A', 314, 2, 'chorshanba'),
            ('ATT-25-12', "O'zbekistonning eng yangi tarixi",     9, 'A', 307, 4, 'chorshanba'),
            ('ATT-25-13', "Ma'lumotlar tuzilmasi va algoritmlar",56, 'A', 314, 1, 'chorshanba'),
            ('ATT-25-13', 'Fizika 2',                           33, 'A', 314, 3, 'chorshanba'),
            ('ATT-25-13', 'Dasturlash asoslari',                54, 'A', 314, 2, 'chorshanba'),

            # ─── PAYSHANBA ───────────────────────────────────────────────────
            ('ATT-25-12', 'Hisob (calculus) 2',                 37, 'A', 217, 1, 'payshanba'),
            ('ATT-25-12', 'Fizika 2',                           29, 'A', 307, 2, 'payshanba'),
            ('ATT-25-13', "O'zbekistonning eng yangi tarixi",    9,  'A', 307, 1, 'payshanba'),
            ('ATT-25-13', 'Hisob (calculus) 2',                 37, 'A', 302, 2, 'payshanba'),

            # ─── JUMA ────────────────────────────────────────────────────────
            ('ATT-25-12', 'Dasturlash 2',                       66,          'A', 112, 2, 'juma'),
            ('ATT-25-13', 'Dasturlash 2',                       ismoilov_f,  'A', 302, 2, 'juma'),
            ('ATT-25-13', 'Hisob (calculus) 2',                 34,          'A', 314, 3, 'juma'),

            # ════════════════════════════════════════════════════════════════
            # RASM 2 — ATT-24-11, ATT-24-12, ATT-24-13  (2-kurs, A-bino)
            # ════════════════════════════════════════════════════════════════

            # ─── DUSHANBA ────────────────────────────────────────────────────
            ('ATT-24-13', 'Differensial tenglamalar',           36,  'A', 112, 2, 'dushanba'),
            ('ATT-24-13', 'Diskret tuzilmalar',                 88,  'A', 214, 3, 'dushanba'),
            ('ATT-24-11', 'Diskret tuzilmalar',                 90,  'A', 214, 3, 'dushanba'),
            ('ATT-24-11', 'Kiberxavfsizlik asoslari',           32,  'A', 214, 4, 'dushanba'),
            ('ATT-24-12', 'Elektron hujjat / Texnologiyalarni boshqarish',
                                                               108, 'A', 226, 4, 'dushanba'),

            # ─── SESHANBA ────────────────────────────────────────────────────
            ('ATT-24-11', 'Differensial tenglamalar',            36, 'A', 301, 3, 'seshanba'),
            ('ATT-24-11', 'Elektron hujjat',                   108, 'A', 301, 1, 'seshanba'),
            ('ATT-24-12', 'Differensial tenglamalar',            36, 'A', 230, 3, 'seshanba'),
            ('ATT-24-12', 'Ehtimollik va statistika (toq)',      44, 'A', 214, 4, 'seshanba'),
            ('ATT-24-12', 'Differensial tenglamalar (juft)',      35, 'A', 214, 4, 'seshanba'),
            ('ATT-24-13', 'Diskret tuzilmalar',            xaniyev_a, 'A', 302, 3, 'seshanba'),
            ('ATT-24-13', 'Server Administration / Stenografik algoritmlar',
                                                               132, 'A', 304, 3, 'seshanba'),

            # ─── CHORSHANBA ──────────────────────────────────────────────────
            ('ATT-24-11', 'Elektron hujjat / Texnologiyalarni boshqarish',
                                                               108, 'A', 314, 1, 'chorshanba'),
            ('ATT-24-12', 'Kiberxavfsizlik asoslari',           32,  'A', 331, 4, 'chorshanba'),
            ('ATT-24-12', 'Ehtimollik va statistika',           44,  'A', 214, 5, 'chorshanba'),
            ('ATT-24-12', 'Ehtimollik va statistika',           35,  'A', 214, 5, 'chorshanba'),
            ('ATT-24-13', 'Kiberxavfsizlik asoslari',           32,  'A', 313, 5, 'chorshanba'),
            ('ATT-24-13', 'Ehtimollik va statistika',           40,  'A', 331, 5, 'chorshanba'),

            # ─── PAYSHANBA ───────────────────────────────────────────────────
            ('ATT-24-12', 'Texnologiyalarni boshqarish',        116, 'A', 331, 3, 'payshanba'),
            ('ATT-24-12', 'Differensial tenglamalar',            36, 'A', 301, 4, 'payshanba'),
            ('ATT-24-12', 'Diskret tuzilmalar',                  88, 'A', 314, 5, 'payshanba'),
            ('ATT-24-13', 'Individual loyiha',                  132, 'A', 304, 1, 'payshanba'),
            ('ATT-24-13', "O'rnatilgan tizimlar",         ismoilov_i, 'A', 227, 2, 'payshanba'),
            ('ATT-24-13', "O'rnatilgan tizimlar",         ismoilov_i, 'A', 227, 3, 'payshanba'),
            ('ATT-24-11', "O'rnatilgan tizimlar (toq)",   ismoilov_i, 'A', 317, 4, 'payshanba'),

            # ─── JUMA ────────────────────────────────────────────────────────
            ('ATT-24-11', 'Kiberxavfsizlik asoslari',           129, 'A', 321, 2, 'juma'),
            ('ATT-24-12', 'Diskret tuzilmalar',                  88, 'A', 301, 3, 'juma'),
            ('ATT-24-12', 'Diskret tuzilmalar',                  32, 'A', 301, 3, 'juma'),
            ('ATT-24-12', 'Kiberxavfsizlik asoslari',            129,'A', 313, 5, 'juma'),
            ('ATT-24-13', 'Differensial tenglamalar',             35, 'A', 301, 3, 'juma'),

            # ════════════════════════════════════════════════════════════════
            # RASM 4 — AKT-23-01, AX-23-08, AX-23-12, RI-23-10  (3-kurs)
            # ════════════════════════════════════════════════════════════════

            # ─── DUSHANBA ────────────────────────────────────────────────────
            ('AKT-23-01', 'Raqamli texnologiya va innovatsiyalar', 108, 'A', 127, 4, 'dushanba'),
            ('AKT-23-01', "STEAM ta'lim",                         120, 'A', 315, 4, 'dushanba'),
            ('AKT-23-01', "STEAM ta'lim",                         116, 'A', 321, 4, 'dushanba'),
            ('AKT-23-01', 'Individual loyiha',                    111, 'A', 321, 5, 'dushanba'),
            ('AX-23-08',  'Tarmoq xavfsizligi (juft)',            132, 'B', 311, 1, 'dushanba'),
            ('AX-23-12',  'Tarmoq xavfsizligi (toq)',             132, 'B', 311, 1, 'dushanba'),
            ('AX-23-12',  'Server Administration',                132, 'B', 230, 2, 'dushanba'),

            # ─── SESHANBA ────────────────────────────────────────────────────
            ('AKT-23-01', 'Individual loyiha',                    111, 'A', 321, 3, 'seshanba'),
            ('AX-23-08',  'Server Administration / Stenografik algoritmlar',
                                                                  132, 'B', 304, 3, 'seshanba'),
            ('AX-23-12',  'Stenografik algoritmlar',              130, 'B', 315, 3, 'seshanba'),
            ('RI-23-10',  'Moliyaviy savodxonlik / Pedagogika',    17, 'A', 201, 4, 'seshanba'),
            ('RI-23-10',  'Moliyaviy savodxonlik / Pedagogika', usmonov_a,'A', 331, 4, 'seshanba'),
            ('RI-23-10',  'Moliyaviy savodxonlik / Pedagogika',    48, 'A', 314, 4, 'seshanba'),
            ('RI-23-10',  'Moliyaviy savodxonlik',                 17, 'A', 201, 5, 'seshanba'),
            ('RI-23-10',  'Moliyaviy savodxonlik',            usmonov_a, 'A', 331, 5, 'seshanba'),
            ('RI-23-10',  'Moliyaviy savodxonlik',                 48, 'A', 314, 5, 'seshanba'),

            # ─── CHORSHANBA ──────────────────────────────────────────────────
            ('AKT-23-01', 'Raqamli texnologiya va innovatsiyalar', 108, 'A', 321, 5, 'chorshanba'),
            ('AX-23-12',  'Stenografik algoritmlar',               134, 'B', 214, 3, 'chorshanba'),
            ('AX-23-12',  'Tarmoq xavfsizligi',                   134, 'B', 314, 4, 'chorshanba'),
            ('AX-23-12',  'Kiberxavfsizlik asoslari',               32, 'B', 301, 5, 'chorshanba'),
            ('RI-23-10',  'Soliq va soliqqa tortish',               21, 'B', 112, 4, 'chorshanba'),
            ('RI-23-10',  'Raqamli iqtisodiyot va innovatsiya',     22, 'B', 217, 5, 'chorshanba'),

            # ─── PAYSHANBA ───────────────────────────────────────────────────
            ('AKT-23-01', "O'rnatilgan tizimlar",            ismoilov_i, 'A', 317, 3, 'payshanba'),
            ('AKT-23-01', "O'rnatilgan tizimlar",            ismoilov_i, 'A', 317, 4, 'payshanba'),
            ('AX-23-08',  'Individual loyiha',                     132, 'B', 304, 1, 'payshanba'),
            ('AX-23-12',  'Individual loyiha',                     129, 'B', 112, 4, 'payshanba'),
            ('AX-23-12',  "O'rnatilgan tizimlar",                   62, 'B', 304, 5, 'payshanba'),
            ('RI-23-10',  'Individual loyiha',                      22, 'B', 112, 2, 'payshanba'),
            ('RI-23-10',  'Moliya bozori (toq)',                    21, 'B', 201, 4, 'payshanba'),
            ('RI-23-10',  "Raqamli iqtisodiyot (toq)",             116, 'B', 217, 4, 'payshanba'),
            ('RI-23-10',  'Soliq va soliqqa tortish',               21, 'B', 217, 5, 'payshanba'),

            # ─── JUMA ────────────────────────────────────────────────────────
            ('AKT-23-01', "STEAM ta'lim",                         120, 'A', 315, 4, 'juma'),
            ('AKT-23-01', "STEAM ta'lim",                         116, 'A', 321, 4, 'juma'),
            ('AX-23-12',  'Kiberxavfsizlik asoslari',              129, 'B', 313, 2, 'juma'),
            ('AX-23-12',  "Diskret tuzilmalar (toq) / Kiberxavfsizlik (juft)", 88, 'B', 301, 3, 'juma'),
            ('AX-23-12',  "Diskret tuzilmalar (toq) / Kiberxavfsizlik (juft)", 32, 'B', 301, 3, 'juma'),
            ('AX-23-12',  'Differensial tenglamalar',               35, 'B', 301, 5, 'juma'),
            ('RI-23-10',  'Individual loyiha',                      22, 'B', 127, 1, 'juma'),
            ('RI-23-10',  'Server Administration',                 132, 'B', 304, 3, 'juma'),
            ('RI-23-10',  'Soliq va soliqqa tortish',               21, 'B', 314, 4, 'juma'),
            ('RI-23-10',  'Moliya bozori',                          21, 'B', 314, 5, 'juma'),
        ]

        d_inserted = 0
        d_errors   = 0
        for guruh, fan, oqituvchi_id, bino, xona, juft, kun in jadval:
            boshlanish, tugash = VAQTLAR[juft]
            try:
                await conn.execute(
                    """INSERT INTO dars_jadvali
                       (oqituvchi_id, kun, boshlanish, tugash,
                        xona_raqam, bino, fan_nomi, guruh)
                       VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
                    oqituvchi_id, kun, boshlanish, tugash,
                    xona, bino, fan, guruh
                )
                d_inserted += 1
            except Exception as e:
                print(f"  XATO [{guruh} {kun} {juft}j]: {e}")
                d_errors += 1

        print(f"  {d_inserted} ta dars qo'shildi, {d_errors} ta xato")

        # ── 4. Tekshirish so'rovi ─────────────────────────────────────────────
        print("\n=== TEKSHIRISH (birinchi 30 qator) ===")
        rows = await conn.fetch(
            """SELECT o.familiya, d.kun, d.boshlanish,
                      d.xona_raqam, d.bino, d.fan_nomi, d.guruh
               FROM dars_jadvali d
               JOIN oqituvchilar o ON o.id = d.oqituvchi_id
               ORDER BY
                   CASE d.kun
                     WHEN 'dushanba'   THEN 1
                     WHEN 'seshanba'   THEN 2
                     WHEN 'chorshanba' THEN 3
                     WHEN 'payshanba'  THEN 4
                     WHEN 'juma'       THEN 5
                   END,
                   d.boshlanish
               LIMIT 30"""
        )
        print(f"{'Familiya':16} {'Kun':10} {'Bosh':5}  {'Xona':6}  {'Fan':38} {'Guruh'}")
        print('-' * 95)
        for r in rows:
            xona = f"{r['bino']}.{r['xona_raqam']}"
            print(
                f"{r['familiya']:16} {r['kun']:10} {str(r['boshlanish'])[:5]}  "
                f"{xona:6}  {r['fan_nomi'][:38]:38} {r['guruh']}"
            )

        # Umumiy statistika
        total_dars  = await conn.fetchval("SELECT COUNT(*) FROM dars_jadvali")
        total_xona  = await conn.fetchval("SELECT COUNT(*) FROM xonalar")
        print(f"\n=== JAMI: {total_dars} ta dars, {total_xona} ta xona ===")

    await pool.close()


if __name__ == '__main__':
    asyncio.run(main())
