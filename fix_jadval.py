"""
Tuzatish:
  1. Rajabov duplikatini o'chirish (seshanba 15:00 xona 201)
  2. Ismoilova F. (id=19) o'rniga Ismoilov I. (id=137) — payshanba 3 ta qator
  3. Xaqberdiyev S. (id=62) — payshanba 4-juft va 5-juft, bazada 'Haqberdiyev' nomi yo'q
  4. Yuldoshev Aziz (id=116) — chorshanba 4-juft va juma 4-juft, bazada 'Yo'ldoshev' nomi yo'q
"""
import asyncio
import asyncpg
from datetime import time as dtime
from config import DB_DSN


async def main():
    conn = await asyncpg.connect(DB_DSN)

    # ── 1. Rajabov duplikatini o'chirish ──────────────────────────
    # seshanba 15:00 xona 201 AKT23-01 — ikkita qolgan, bittasini o'chiramiz
    dup_ids = await conn.fetch(
        """SELECT d.id FROM dars_jadvali d
           JOIN oqituvchilar o ON o.id = d.oqituvchi_id
           WHERE o.familiya ILIKE 'Rajabov%'
             AND d.guruh = 'AKT23-01'
             AND d.kun = 'seshanba'
             AND d.boshlanish = '15:00'
             AND d.xona_raqam = 201
           ORDER BY d.id"""
    )
    if len(dup_ids) > 1:
        await conn.execute("DELETE FROM dars_jadvali WHERE id = $1", dup_ids[0]['id'])
        print(f"[FIX] Rajabov duplikati o'chirildi (id={dup_ids[0]['id']})")
    else:
        print(f"[OK]  Rajabov duplikat yo'q ({len(dup_ids)} ta)")

    # ── 2. Ismoilova o'chirib, Ismoilov I. kiritish ───────────────
    # 3 ta yozuv: payshanba 10:00, 11:30, 13:30
    ismoilova_id = 19  # Ismoilova F.
    ismoilov_id  = 137  # Ismoilov I.

    wrong = await conn.fetch(
        """SELECT id, kun, boshlanish, xona_raqam FROM dars_jadvali
           WHERE oqituvchi_id = $1 AND guruh = 'AKT23-01'
             AND kun = 'payshanba'""",
        ismoilova_id,
    )
    for row in wrong:
        await conn.execute("DELETE FROM dars_jadvali WHERE id = $1", row['id'])
        print(f"[FIX] Ismoilova qatori o'chirildi: payshanba {str(row['boshlanish'])[:5]} xona {row['xona_raqam']}")

    # To'g'ri qatorlarni kiritish
    darslar_ismoilov = [
        (227, dtime(10, 0),  dtime(11, 20)),
        (227, dtime(11, 30), dtime(12, 50)),
        (317, dtime(13, 30), dtime(14, 50)),
    ]
    for xona, bosh, tug in darslar_ismoilov:
        await conn.execute(
            """INSERT INTO dars_jadvali
               (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
               VALUES ($1, $2, 'A', $3, 'AKT23-01', 'payshanba', $4, $5)""",
            ismoilov_id, xona, "O'rnatilgan tizimlar", bosh, tug,
        )
        print(f"[INS] Ismoilov I. | AKT23-01 | payshanba {bosh}-{tug} xona {xona}")

    # ── 3. Xaqberdiyev S. — payshanba 4-juft va 5-juft ───────────
    xaqberdiyev_id = 62
    darslar_xaq = [
        ("AX23-08", 127, dtime(13, 30), dtime(14, 50), "O'rnatilgan tizimlar"),
        ("AX23-08", 304, dtime(15,  0), dtime(16, 20), "O'rnatilgan tizimlar"),
    ]
    for guruh, xona, bosh, tug, fan in darslar_xaq:
        await conn.execute(
            """INSERT INTO dars_jadvali
               (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
               VALUES ($1, $2, 'A', $3, $4, 'payshanba', $5, $6)""",
            xaqberdiyev_id, xona, fan, guruh, bosh, tug,
        )
        print(f"[INS] Xaqberdiyev S. | {guruh} | payshanba {bosh}-{tug} xona {xona}")

    # ── 4. Yuldoshev Aziz — chorshanba 4-juft va juma 4-juft ─────
    yuldoshev_id = 116
    darslar_yul = [
        ("AKT23-01", 226, "chorshanba", dtime(13, 30), dtime(14, 50), "Kreativ pedagogika/STEAM ta'lim"),
        ("AKT23-01", 321, "juma",       dtime(13, 30), dtime(14, 50), "Kreativ pedagogika/STEAM ta'lim"),
    ]
    for guruh, xona, kun, bosh, tug, fan in darslar_yul:
        await conn.execute(
            """INSERT INTO dars_jadvali
               (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
               VALUES ($1, $2, 'A', $3, $4, $5, $6, $7)""",
            yuldoshev_id, xona, fan, guruh, kun, bosh, tug,
        )
        print(f"[INS] Yuldoshev Aziz | {guruh} | {kun} {bosh}-{tug} xona {xona}")

    # ── Yakuniy tekshiruv ──────────────────────────────────────────
    print("\n" + "=" * 65)
    print("YAKUNIY JADVAL")
    print("=" * 65)
    rows = await conn.fetch(
        """SELECT o.familiya, d.guruh, d.kun, d.boshlanish, d.tugash,
                  d.xona_raqam, d.fan_nomi
           FROM dars_jadvali d
           JOIN oqituvchilar o ON o.id = d.oqituvchi_id
           WHERE d.bino = 'A'
             AND d.guruh IN ('AKT23-01','AX23-08','AX23-12','RI23-10')
           ORDER BY
             d.guruh,
             CASE d.kun
               WHEN 'dushanba' THEN 1 WHEN 'seshanba' THEN 2
               WHEN 'chorshanba' THEN 3 WHEN 'payshanba' THEN 4
               WHEN 'juma' THEN 5
             END,
             d.boshlanish"""
    )
    prev = None
    for r in rows:
        if r['guruh'] != prev:
            print(f"\n  [{r['guruh']}]")
            prev = r['guruh']
        b = str(r['boshlanish'])[:5]
        t_ = str(r['tugash'])[:5]
        print(f"    {r['kun']:<12} {b}-{t_}  xona {r['xona_raqam']}  {r['familiya']:<18}  {r['fan_nomi']}")

    print(f"\nJami: {len(rows)} ta qator")
    await conn.close()


asyncio.run(main())
