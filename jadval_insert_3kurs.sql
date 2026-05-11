-- ═══════════════════════════════════════════════════════════════════
-- TATU SF — 3-KURS DARS JADVALI
-- Guruhlar: AKT23-01, AX23-08, AX23-12, RI23-10  |  Bino: A
-- Kiritilmagan: Mustaqil ta'lim, Marifat darsi, Tyutorlik soati
-- toq/juft hafta → har biri 1 ta INSERT
-- Jami: 31 ta INSERT
-- ═══════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────
-- 1-QADAM: O'QITUVCHILAR MAVJUDLIGINI TEKSHIR
-- ───────────────────────────────────────────────────────────────────
SELECT id, familiya, ism FROM oqituvchilar ORDER BY familiya;


-- ───────────────────────────────────────────────────────────────────
-- 2-QADAM: INSERT — SESHANBA  (3 ta)
-- ───────────────────────────────────────────────────────────────────

-- AKT23-01 | 5-juft 15:00-16:20 | A.201 | Moliyaviy savodxonlik
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 201, 'A', 'Moliyaviy savodxonlik', 'AKT23-01',
       'seshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Rajabov%' LIMIT 1;

-- AKT23-01 | 5-juft 15:00-16:20 | A.331 | Pedagogika
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 331, 'A', 'Pedagogika', 'AKT23-01',
       'seshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Usmonov%' LIMIT 1;

-- AKT23-01 | 5-juft 15:00-16:20 | A.314 | Atrof-muhit
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 314, 'A', 'Atrof-muhit', 'AKT23-01',
       'seshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Fozilov%' LIMIT 1;


-- ───────────────────────────────────────────────────────────────────
-- INSERT — CHORSHANBA  (7 ta)
-- ───────────────────────────────────────────────────────────────────

-- AKT23-01 | 4-juft 13:30-14:50 | A.127 | Kreativ pedagogika/STEAM ta'lim
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 127, 'A', 'Kreativ pedagogika/STEAM ta''lim', 'AKT23-01',
       'chorshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Muhammadiyev%' LIMIT 1;

-- AKT23-01 | 4-juft 13:30-14:50 | A.226 | Kreativ pedagogika/STEAM ta'lim
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 226, 'A', 'Kreativ pedagogika/STEAM ta''lim', 'AKT23-01',
       'chorshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Yo%ldoshev%' LIMIT 1;

-- AX23-08 | 4-juft 13:30-14:50 | A.214 | Stenografik algoritmlar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 214, 'A', 'Stenografik algoritmlar', 'AX23-08',
       'chorshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Nishonova%' LIMIT 1;

-- RI23-10 | 4-juft 13:30-14:50 | A.112 | Soliq va soliqqa tortish
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 112, 'A', 'Soliq va soliqqa tortish', 'RI23-10',
       'chorshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Togayeva%' LIMIT 1;

-- AKT23-01 | 5-juft 15:00-16:20 | A.321 | Raqamli texnologiya va innovatsiyalar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 321, 'A', 'Raqamli texnologiya va innovatsiyalar', 'AKT23-01',
       'chorshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Shodmonov%' LIMIT 1;

-- AX23-12 | 5-juft 15:00-16:20 | A.314 | Tarmoq xavfsizligi
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 314, 'A', 'Tarmoq xavfsizligi', 'AX23-12',
       'chorshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Nishonova%' LIMIT 1;

-- RI23-10 | 5-juft 15:00-16:20 | A.217 | Raqamli iqtisodiyot va innovatsiya
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 217, 'A', 'Raqamli iqtisodiyot va innovatsiya', 'RI23-10',
       'chorshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Baxodirov%' LIMIT 1;


-- ───────────────────────────────────────────────────────────────────
-- INSERT — PAYSHANBA  (13 ta)
-- ───────────────────────────────────────────────────────────────────

-- AX23-08 | 1-juft 08:30-09:50 | A.304 | Individual loyiha
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 304, 'A', 'Individual loyiha', 'AX23-08',
       'payshanba', '08:30', '09:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Kiyamov%' LIMIT 1;

-- AKT23-01 | 2-juft 10:00-11:20 | A.227 | O'rnatilgan tizimlar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 227, 'A', 'O''rnatilgan tizimlar', 'AKT23-01',
       'payshanba', '10:00', '11:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Ismoilov%' LIMIT 1;

-- AX23-12 | 2-juft 10:00-11:20 | A.112 | Individual loyiha
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 112, 'A', 'Individual loyiha', 'AX23-12',
       'payshanba', '10:00', '11:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Baxodirov%' LIMIT 1;

-- AKT23-01 | 3-juft 11:30-12:50 | A.227 | O'rnatilgan tizimlar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 227, 'A', 'O''rnatilgan tizimlar', 'AKT23-01',
       'payshanba', '11:30', '12:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Ismoilov%' LIMIT 1;

-- AX23-12 | 3-juft 11:30-12:50 | A.217 | Raqamli iqtisodiyot va innovatsiya
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 217, 'A', 'Raqamli iqtisodiyot va innovatsiya', 'AX23-12',
       'payshanba', '11:30', '12:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Baxodirov%' LIMIT 1;

-- AKT23-01 | 4-juft 13:30-14:50 | A.317 | O'rnatilgan tizimlar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 317, 'A', 'O''rnatilgan tizimlar', 'AKT23-01',
       'payshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Ismoilov%' LIMIT 1;

-- AX23-08 | 4-juft 13:30-14:50 | A.127 | O'rnatilgan tizimlar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 127, 'A', 'O''rnatilgan tizimlar', 'AX23-08',
       'payshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Haqberdiyev%' LIMIT 1;

-- AX23-12 | 4-juft 13:30-14:50 | A.112 | Individual loyiha
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 112, 'A', 'Individual loyiha', 'AX23-12',
       'payshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Shakarov%' LIMIT 1;

-- RI23-10 | 4-juft 13:30-14:50 | A.201 | Moliya bozori  (toq hafta — 1 INSERT)
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 201, 'A', 'Moliya bozori', 'RI23-10',
       'payshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Togayeva%' LIMIT 1;

-- RI23-10 | 4-juft 13:30-14:50 | A.201 | Soliq va soliqqa tortish  (juft hafta — 1 INSERT)
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 201, 'A', 'Soliq va soliqqa tortish', 'RI23-10',
       'payshanba', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Togayeva%' LIMIT 1;

-- AKT23-01 | 5-juft 15:00-16:20 | A.321 | Raqamli texnologiya va innovatsiyalar  (juft hafta — 1 INSERT)
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 321, 'A', 'Raqamli texnologiya va innovatsiyalar', 'AKT23-01',
       'payshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Shodmonov%' LIMIT 1;

-- AX23-08 | 5-juft 15:00-16:20 | A.304 | O'rnatilgan tizimlar
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 304, 'A', 'O''rnatilgan tizimlar', 'AX23-08',
       'payshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Haqberdiyev%' LIMIT 1;

-- RI23-10 | 5-juft 15:00-16:20 | A.331 | Moliya bozori
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 331, 'A', 'Moliya bozori', 'RI23-10',
       'payshanba', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Togayeva%' LIMIT 1;


-- ───────────────────────────────────────────────────────────────────
-- INSERT — JUMA  (8 ta)
-- ───────────────────────────────────────────────────────────────────

-- AX23-12 | 1-juft 08:30-09:50 | A.304 | Individual loyiha
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 304, 'A', 'Individual loyiha', 'AX23-12',
       'juma', '08:30', '09:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Shakarov%' LIMIT 1;

-- AX23-08 | 2-juft 10:00-11:20 | A.301 | Individual loyiha
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 301, 'A', 'Individual loyiha', 'AX23-08',
       'juma', '10:00', '11:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Kiyamov%' LIMIT 1;

-- AX23-08 | 3-juft 11:30-12:50 | A.304 | Server Administration
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 304, 'A', 'Server Administration', 'AX23-08',
       'juma', '11:30', '12:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Kiyamov%' LIMIT 1;

-- AX23-12 | 3-juft 11:30-12:50 | A.127 | Individual loyiha
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 127, 'A', 'Individual loyiha', 'AX23-12',
       'juma', '11:30', '12:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Baxodirov%' LIMIT 1;

-- AKT23-01 | 4-juft 13:30-14:50 | A.315 | Kreativ pedagogika/STEAM ta'lim
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 315, 'A', 'Kreativ pedagogika/STEAM ta''lim', 'AKT23-01',
       'juma', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Mamanazarov%' LIMIT 1;

-- AKT23-01 | 4-juft 13:30-14:50 | A.321 | Kreativ pedagogika/STEAM ta'lim
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 321, 'A', 'Kreativ pedagogika/STEAM ta''lim', 'AKT23-01',
       'juma', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Yo%ldoshev%' LIMIT 1;

-- RI23-10 | 4-juft 13:30-14:50 | A.314 | Soliq va soliqqa tortish
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 314, 'A', 'Soliq va soliqqa tortish', 'RI23-10',
       'juma', '13:30', '14:50'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Togayeva%' LIMIT 1;

-- RI23-10 | 5-juft 15:00-16:20 | A.314 | Moliya bozori
INSERT INTO dars_jadvali
  (oqituvchi_id, xona_raqam, bino, fan_nomi, guruh, kun, boshlanish, tugash)
SELECT o.id, 314, 'A', 'Moliya bozori', 'RI23-10',
       'juma', '15:00', '16:20'
FROM oqituvchilar o WHERE o.familiya ILIKE 'Togayeva%' LIMIT 1;


-- ───────────────────────────────────────────────────────────────────
-- 3-QADAM: TEKSHIRISH
-- ───────────────────────────────────────────────────────────────────
SELECT
  o.familiya,
  d.guruh,
  d.kun,
  d.boshlanish,
  d.tugash,
  d.xona_raqam,
  d.fan_nomi
FROM dars_jadvali d
JOIN oqituvchilar o ON o.id = d.oqituvchi_id
WHERE d.bino = 'A'
  AND d.guruh IN ('AKT23-01', 'AX23-08', 'AX23-12', 'RI23-10')
ORDER BY
  d.guruh,
  CASE d.kun
    WHEN 'dushanba'   THEN 1
    WHEN 'seshanba'   THEN 2
    WHEN 'chorshanba' THEN 3
    WHEN 'payshanba'  THEN 4
    WHEN 'juma'       THEN 5
  END,
  d.boshlanish;
