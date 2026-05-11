import asyncpg
from datetime import datetime, time as dtime
from config import DB_DSN

KUNLAR = {0: 'dushanba', 1: 'seshanba', 2: 'chorshanba', 3: 'payshanba', 4: 'juma'}

JUFT_VAQTLAR = {
    1: ('08:30', '09:50'), 2: ('10:00', '11:20'), 3: ('11:30', '12:50'),
    4: ('13:30', '14:50'), 5: ('15:00', '16:20'), 6: ('16:30', '17:50'),
}
BOSH_VAQT_TO_JUFT = {bosh: n for n, (bosh, _) in JUFT_VAQTLAR.items()}


def bugungi_kun() -> str | None:
    return KUNLAR.get(datetime.now().weekday())


def hozirgi_juft() -> int | None:
    hozir = datetime.now().strftime('%H:%M')
    for n, (bosh, tug) in JUFT_VAQTLAR.items():
        if bosh <= hozir <= tug:
            return n
    return None


# ─── Ulanish ────────────────────────────────────────────────────────────────

async def create_pool():
    return await asyncpg.create_pool(DB_DSN)


# ─── 1-guruh: Foydalanuvchi ──────────────────────────────────────────────────

async def get_user(pool, telegram_id) -> dict | None:
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "SELECT * FROM foydalanuvchilar WHERE telegram_id = $1", telegram_id
            )
            return dict(row) if row else None
        except Exception as e:
            print(f"DB xato: {e}")
            return None


async def create_user(pool, telegram_id, telegram_username, ism, familiya, tel_raqam) -> int | None:
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """INSERT INTO foydalanuvchilar (telegram_id, ism, familiya, tel_raqam)
                   VALUES ($1, $2, $3, $4)
                   ON CONFLICT (telegram_id) DO NOTHING
                   RETURNING id""",
                telegram_id, ism, familiya, tel_raqam
            )
            return row["id"] if row else None
        except Exception as e:
            print(f"DB xato: {e}")
            return None


async def update_user_tel(pool, telegram_id, tel) -> None:
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "UPDATE foydalanuvchilar SET tel_raqam = $1 WHERE telegram_id = $2",
                tel, telegram_id
            )
        except Exception as e:
            print(f"DB xato: {e}")


# ─── 2-guruh: Kafedralar ─────────────────────────────────────────────────────

async def get_kafedralar_by_bino(pool, bino) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                "SELECT * FROM kafedralar WHERE bino = $1 ORDER BY id", bino
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_all_kafedralar(pool) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("SELECT * FROM kafedralar ORDER BY id")
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_kafedra(pool, kafedra_id) -> dict | None:
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "SELECT * FROM kafedralar WHERE id = $1", kafedra_id
            )
            return dict(row) if row else None
        except Exception as e:
            print(f"DB xato: {e}")
            return None


async def get_kafedra_oqituvchilari(pool, kafedra_id) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT * FROM oqituvchilar
                   WHERE kafedra_id = $1 AND faol = TRUE
                   ORDER BY familiya""",
                kafedra_id
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


# ─── 3-guruh: O'qituvchilar ──────────────────────────────────────────────────

async def get_oqituvchi(pool, oqituvchi_id) -> dict | None:
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """SELECT o.*,
                          k.nomi        AS kafedra_nomi,
                          k.xona_raqam  AS kafedra_xona_raqam,
                          k.bino        AS kafedra_bino
                   FROM oqituvchilar o
                   LEFT JOIN kafedralar k ON k.id = o.kafedra_id
                   WHERE o.id = $1""",
                oqituvchi_id
            )
            return dict(row) if row else None
        except Exception as e:
            print(f"DB xato: {e}")
            return None


async def get_oqituvchi_bugungi_dars(pool, oqituvchi_id) -> list[dict]:
    # Bugungi kun nomi aniqlanadi (0=dushanba ... 4=juma)
    kun_index = datetime.now().weekday()
    bugun = KUNLAR.get(kun_index)
    if not bugun:
        return []
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT * FROM dars_jadvali
                   WHERE oqituvchi_id = $1 AND kun = $2
                   ORDER BY boshlanish""",
                oqituvchi_id, bugun
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_oqituvchi_by_search(pool, query) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT * FROM oqituvchilar
                   WHERE (familiya ILIKE $1 OR ism ILIKE $1) AND faol = TRUE
                   ORDER BY familiya
                   LIMIT 5""",
                f"%{query}%"
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def create_oqituvchi(pool, kafedra_id, ism, familiya,
                           otasining_ismi, tel_raqam, telegram_username,
                           xona_raqam, bino) -> int | None:
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """INSERT INTO oqituvchilar
                   (kafedra_id, ism, familiya, otasining_ismi, tel_raqam,
                    telegram_username, xona_raqam, bino)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                   RETURNING id""",
                kafedra_id, ism, familiya, otasining_ismi, tel_raqam,
                telegram_username, xona_raqam, bino
            )
            return row["id"] if row else None
        except Exception as e:
            print(f"DB xato: {e}")
            return None


async def update_oqituvchi(pool, oqituvchi_id, maydon, qiymat) -> None:
    # Maydon nomi dinamik — faqat ruxsat etilgan maydonlar yangilanadi
    ruxsat_etilgan = {
        'ism', 'familiya', 'otasining_ismi', 'tel_raqam',
        'telegram_username', 'telegram_file_id', 'xona_raqam',
        'bino', 'kafedra_id', 'faol'
    }
    if maydon not in ruxsat_etilgan:
        print(f"DB xato: '{maydon}' maydonini yangilash ruxsat etilmagan")
        return
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                f"UPDATE oqituvchilar SET {maydon} = $1 WHERE id = $2",
                qiymat, oqituvchi_id
            )
        except Exception as e:
            print(f"DB xato: {e}")


async def delete_oqituvchi(pool, oqituvchi_id) -> None:
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "UPDATE oqituvchilar SET faol = FALSE WHERE id = $1", oqituvchi_id
            )
        except Exception as e:
            print(f"DB xato: {e}")


# ─── 4-guruh: Dars jadvali ───────────────────────────────────────────────────

async def get_oqituvchi_jadval(pool, oqituvchi_id) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT * FROM dars_jadvali
                   WHERE oqituvchi_id = $1
                   ORDER BY
                       CASE kun
                           WHEN 'dushanba'  THEN 1
                           WHEN 'seshanba'  THEN 2
                           WHEN 'chorshanba' THEN 3
                           WHEN 'payshanba' THEN 4
                           WHEN 'juma'      THEN 5
                       END,
                       boshlanish""",
                oqituvchi_id
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


def _parse_time(t) -> dtime:
    if isinstance(t, dtime):
        return t
    h, m = map(int, str(t).split(':'))
    return dtime(h, m)


async def create_dars(pool, oqituvchi_id, kun, boshlanish,
                      tugash, xona_raqam, bino, fan_nomi, guruh) -> bool:
    bosh_t = _parse_time(boshlanish)
    tug_t = _parse_time(tugash)
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """INSERT INTO dars_jadvali
                   (oqituvchi_id, kun, boshlanish, tugash,
                    xona_raqam, bino, fan_nomi, guruh)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                oqituvchi_id, kun, bosh_t, tug_t,
                xona_raqam, bino, fan_nomi, guruh
            )
            return True
        except Exception as e:
            print(f"DB xato: {e}")
            return False


async def delete_dars(pool, dars_id) -> None:
    async with pool.acquire() as conn:
        try:
            await conn.execute("DELETE FROM dars_jadvali WHERE id = $1", dars_id)
        except Exception as e:
            print(f"DB xato: {e}")


# ─── 5-guruh: Xonalar ────────────────────────────────────────────────────────

async def get_xonalar(pool, bino, qavat) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT * FROM xonalar
                   WHERE bino = $1 AND qavat = $2
                   ORDER BY raqam""",
                bino, qavat
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_xona_tafsilot(pool, raqam, bino) -> dict | None:
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                "SELECT * FROM xonalar WHERE raqam = $1 AND bino = $2",
                raqam, bino
            )
            return dict(row) if row else None
        except Exception as e:
            print(f"DB xato: {e}")
            return None


async def get_qavat_xonalari(pool, bino: str, qavat: int) -> list[dict]:
    bugun = bugungi_kun()
    hozir = datetime.now().time() if bugun else None
    async with pool.acquire() as conn:
        try:
            if bugun and hozir:
                rows = await conn.fetch(
                    """SELECT x.*,
                       EXISTS(
                           SELECT 1 FROM dars_jadvali d
                           WHERE d.xona_raqam = x.raqam AND d.bino = x.bino
                             AND d.kun = $3
                             AND $4 BETWEEN d.boshlanish AND d.tugash
                       ) AS dars_band
                       FROM xonalar x
                       WHERE x.bino = $1 AND x.qavat = $2
                       ORDER BY x.raqam""",
                    bino, qavat, bugun, hozir
                )
            else:
                rows = await conn.fetch(
                    """SELECT x.*, FALSE AS dars_band
                       FROM xonalar x
                       WHERE x.bino = $1 AND x.qavat = $2
                       ORDER BY x.raqam""",
                    bino, qavat
                )
            result = []
            for r in rows:
                d = dict(r)
                d['holat'] = 'band' if (d.get('dars_band') or d.get('band')) else 'bosh'
                result.append(d)
            return result
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_xona_bugungi_jadval(pool, raqam: int, bino: str) -> list[dict]:
    bugun = bugungi_kun()
    if not bugun:
        return []
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT d.id, d.boshlanish, d.tugash, d.fan_nomi, d.guruh,
                          o.id AS oqituvchi_id, o.familiya, o.ism
                   FROM dars_jadvali d
                   JOIN oqituvchilar o ON o.id = d.oqituvchi_id
                   WHERE d.xona_raqam = $1 AND d.bino = $2 AND d.kun = $3
                   ORDER BY d.boshlanish""",
                raqam, bino, bugun
            )
            result = []
            for r in rows:
                d = dict(r)
                d['juft_raqami'] = BOSH_VAQT_TO_JUFT.get(str(d['boshlanish'])[:5])
                result.append(d)
            return result
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_xona_kun_jadvali(pool, raqam: int, bino: str, kun: str) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT d.id, d.boshlanish, d.tugash, d.fan_nomi, d.guruh,
                          o.id AS oqituvchi_id, o.familiya, o.ism
                   FROM dars_jadvali d
                   JOIN oqituvchilar o ON o.id = d.oqituvchi_id
                   WHERE d.xona_raqam = $1 AND d.bino = $2 AND d.kun = $3
                   ORDER BY d.boshlanish""",
                raqam, bino, kun
            )
            result = []
            for r in rows:
                d = dict(r)
                d['juft_raqami'] = BOSH_VAQT_TO_JUFT.get(str(d['boshlanish'])[:5])
                result.append(d)
            return result
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_xona_haftalik_jadval(pool, raqam: int, bino: str) -> dict:
    kun_tartibi = ['dushanba', 'seshanba', 'chorshanba', 'payshanba', 'juma']
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT d.boshlanish, d.tugash, d.fan_nomi, d.guruh, d.kun,
                          o.id AS oqituvchi_id, o.familiya, o.ism
                   FROM dars_jadvali d
                   JOIN oqituvchilar o ON o.id = d.oqituvchi_id
                   WHERE d.xona_raqam = $1 AND d.bino = $2
                   ORDER BY
                       CASE d.kun
                           WHEN 'dushanba' THEN 1 WHEN 'seshanba' THEN 2
                           WHEN 'chorshanba' THEN 3 WHEN 'payshanba' THEN 4
                           WHEN 'juma' THEN 5
                       END, d.boshlanish""",
                raqam, bino
            )
            result = {k: [] for k in kun_tartibi}
            for r in rows:
                d = dict(r)
                d['juft_raqami'] = BOSH_VAQT_TO_JUFT.get(str(d['boshlanish'])[:5])
                result[d['kun']].append(d)
            return result
        except Exception as e:
            print(f"DB xato: {e}")
            return {k: [] for k in kun_tartibi}


async def create_xona(pool, raqam, bino, qavat) -> None:
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """INSERT INTO xonalar (raqam, bino, qavat)
                   VALUES ($1, $2, $3)""",
                raqam, bino, qavat
            )
        except Exception as e:
            print(f"DB xato: {e}")


async def set_xona_holat(pool, raqam, bino, band, band_gacha=None) -> None:
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """UPDATE xonalar
                   SET band = $1, band_gacha = $2
                   WHERE raqam = $3 AND bino = $4""",
                band, band_gacha, raqam, bino
            )
        except Exception as e:
            print(f"DB xato: {e}")


# ─── 6-guruh: Statistika va log ──────────────────────────────────────────────

async def get_all_stats(pool) -> dict:
    async with pool.acquire() as conn:
        try:
            bugun = datetime.now().date()
            bugun_sorovlar = await conn.fetchval(
                "SELECT COUNT(*) FROM loglar WHERE vaqt::date = $1", bugun
            )
            faol_foydalanuvchilar = await conn.fetchval(
                "SELECT COUNT(DISTINCT telegram_id) FROM loglar WHERE vaqt::date = $1", bugun
            )
            jami_foydalanuvchilar = await conn.fetchval(
                "SELECT COUNT(*) FROM foydalanuvchilar"
            )
            jami_oqituvchilar = await conn.fetchval(
                "SELECT COUNT(*) FROM oqituvchilar WHERE faol = TRUE"
            )
            return {
                "bugun_sorovlar": bugun_sorovlar or 0,
                "faol_foydalanuvchilar": faol_foydalanuvchilar or 0,
                "jami_foydalanuvchilar": jami_foydalanuvchilar or 0,
                "jami_oqituvchilar": jami_oqituvchilar or 0,
            }
        except Exception as e:
            print(f"DB xato: {e}")
            return {}


async def log_sorov(pool, telegram_id, matn) -> None:
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO loglar (telegram_id, tur, matn) VALUES ($1, 'sorov', $2)",
                telegram_id, matn
            )
        except Exception as e:
            print(f"DB xato: {e}")


async def get_haftalik_hisobot(pool) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT
                       DATE(vaqt)                       AS kun,
                       COUNT(*)                         AS sorovlar,
                       COUNT(DISTINCT telegram_id)      AS faol_users
                   FROM loglar
                   WHERE vaqt >= NOW() - INTERVAL '7 days'
                   GROUP BY DATE(vaqt)
                   ORDER BY kun"""
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def get_all_foydalanuvchilar(pool, offset: int = 0, limit: int = 10) -> tuple[list[dict], int]:
    async with pool.acquire() as conn:
        try:
            jami = await conn.fetchval("SELECT COUNT(*) FROM foydalanuvchilar") or 0
            rows = await conn.fetch(
                """SELECT id, telegram_id, ism, familiya, tel_raqam
                   FROM foydalanuvchilar
                   ORDER BY id
                   LIMIT $1 OFFSET $2""",
                limit, offset,
            )
            return [dict(r) for r in rows], jami
        except Exception as e:
            print(f"DB xato: {e}")
            return [], 0


async def get_recent_errors(pool, limit=5) -> list[dict]:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(
                """SELECT * FROM loglar
                   WHERE tur = 'xato'
                   ORDER BY vaqt DESC
                   LIMIT $1""",
                limit
            )
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB xato: {e}")
            return []


async def send_broadcast(pool, bot, matn) -> dict:
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("SELECT telegram_id FROM foydalanuvchilar")
        except Exception as e:
            print(f"DB xato: {e}")
            return {"yuborildi": 0, "xato": 0}

    yuborildi = 0
    xato = 0
    for row in rows:
        try:
            await bot.send_message(row["telegram_id"], matn)
            yuborildi += 1
        except Exception:
            xato += 1
    return {"yuborildi": yuborildi, "xato": xato}


# ─── Test bloki ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    from config import DB_DSN

    async def test():
        pool = await create_pool()
        print("✅ Baza ulanishi ishlayapti")
        kafedralar = await get_all_kafedralar(pool)
        print(f"✅ Kafedralar: {len(kafedralar)} ta")
        await pool.close()

    asyncio.run(test())
