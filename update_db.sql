-- ════════════════════════════════════════════════════════
-- 1-QADAM: KAFEDRALAR BINO YANGILASH
-- ════════════════════════════════════════════════════════

-- A-bino (allaqachon to'g'ri, lekin aniq qilib yozamiz)
UPDATE kafedralar SET bino='A'
WHERE nomi IN (
  'Tillar',
  'Telekommunikatsiya injiniringi',
  'Raqamli va ta''lim texnologiyalari',
  'Axborot xavfsizligi'
);

-- B-bino (oldin A edi, endi B ga o'tkazamiz)
UPDATE kafedralar SET bino='B'
WHERE nomi IN (
  'Ijtimoiy gumanitar-1',
  'Ijtimoiy gumanitar-2',
  'Tabiiy fanlar',
  'Axborot texnologiyalari',
  'Dasturiy injiniring',
  'Kompyuter tizimlari'
);

-- ════════════════════════════════════════════════════════
-- 2-QADAM: LAVOZIM USTUNI QO'SHISH
-- ════════════════════════════════════════════════════════

ALTER TABLE oqituvchilar ADD COLUMN IF NOT EXISTS lavozim TEXT;

-- ════════════════════════════════════════════════════════
-- 3-QADAM: TILLAR KAFEDRASI (kafedra_id=1)
-- ════════════════════════════════════════════════════════

-- Asosiy (штат)
UPDATE oqituvchilar SET familiya='Toyirova',   ism='Dilfuza',    lavozim='штат', bino='A' WHERE id=1;
UPDATE oqituvchilar SET familiya='Xotamov',    ism='Nurbek',     lavozim='штат', bino='A' WHERE id=2;
UPDATE oqituvchilar SET familiya='Raxmatova',  ism='Saodat',     lavozim='штат', bino='A' WHERE id=3;
UPDATE oqituvchilar SET familiya='Ibatova',    ism='Amira',      lavozim='штат', bino='A' WHERE id=4;
UPDATE oqituvchilar SET familiya='Toshpulatov',ism='Dilshod',    lavozim='штат', bino='A' WHERE id=5;
UPDATE oqituvchilar SET familiya='Narziyeva',  ism='Gulnoza',    lavozim='штат', bino='A' WHERE id=6;
UPDATE oqituvchilar SET familiya='Akromova',   ism='Moxichexra', lavozim='штат', bino='A' WHERE id=7;

-- Ichki o'rindosh (YANGI)
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, bino, faol, lavozim) VALUES
  (1, 'Djalilova', 'Gulbahor', 'A', TRUE, 'ички');

-- Tashqi o'rindosh (YANGI)
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, bino, faol, lavozim) VALUES
  (1, 'Abdiyev',  'Murodqosim', 'A', TRUE, 'ташки'),
  (1, 'Kabilova', 'Gulchexra',  'A', TRUE, 'ташки');

-- ════════════════════════════════════════════════════════
-- 4-QADAM: TELEKOMMUNIKATSIYA INJINIRINGI (kafedra_id=8)
-- ════════════════════════════════════════════════════════

-- Asosiy (штат)
UPDATE oqituvchilar SET familiya='Mirzoqulov',  ism='Xotam',        lavozim='штат', bino='A' WHERE id=93;
UPDATE oqituvchilar SET familiya='Jumanov',     ism='Haqberdi',     lavozim='штат', bino='A' WHERE id=94;
UPDATE oqituvchilar SET familiya='Kilichev',    ism='Jasur',        lavozim='штат', bino='A' WHERE id=95;
UPDATE oqituvchilar SET familiya='Xotamov',     ism='Abdugafur',    lavozim='штат', bino='A' WHERE id=96;
UPDATE oqituvchilar SET familiya='Bolbekov',    ism='Ma''ruf',      lavozim='штат', bino='A' WHERE id=97;
UPDATE oqituvchilar SET familiya='Xidirov',     ism='Abduvali',     lavozim='штат', bino='A' WHERE id=98;
UPDATE oqituvchilar SET familiya='Nurmurodov',  ism='Jasur',        lavozim='штат', bino='A' WHERE id=99;
UPDATE oqituvchilar SET familiya='Jumaboyev',   ism='Tuyg''un',     lavozim='штат', bino='A' WHERE id=100;
UPDATE oqituvchilar SET familiya='Nizamov',     ism='Akram',        lavozim='штат', bino='A' WHERE id=101;
UPDATE oqituvchilar SET familiya='O''rinov',    ism='Jamshid',      lavozim='штат', bino='A' WHERE id=102;
UPDATE oqituvchilar SET familiya='G''ayratov',  ism='Zafarjon',     lavozim='штат', bino='A' WHERE id=103;
UPDATE oqituvchilar SET familiya='Xodjayev',    ism='Muhammadzoir', lavozim='штат', bino='A' WHERE id=104;
UPDATE oqituvchilar SET familiya='Djurayev',    ism='Adiljon',      lavozim='штат', bino='A' WHERE id=106;

-- Tashqi o'rindosh: id=105 allaqachon bor (G'aybullayev A.)
UPDATE oqituvchilar SET familiya='Gaybullayev', ism='Alisher', lavozim='ташки', bino='A' WHERE id=105;

-- Tashqi o'rindosh (YANGI)
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, bino, faol, lavozim) VALUES
  (8, 'Mavlonov', 'Urin',    'A', TRUE, 'ташки'),
  (8, 'Raximov',  'Alisher', 'A', TRUE, 'ташки');

-- ════════════════════════════════════════════════════════
-- 5-QADAM: RAQAMLI VA TA'LIM TEXNOLOGIYALARI (kafedra_id=9)
-- ════════════════════════════════════════════════════════

-- Asosiy (штат)
UPDATE oqituvchilar SET familiya='Raxmonov',    ism='Xoshim',   lavozim='штат', bino='A' WHERE id=107;
UPDATE oqituvchilar SET familiya='Xoliyarova',  ism='Feruza',   lavozim='штат', bino='A' WHERE id=114;
UPDATE oqituvchilar SET familiya='Ganiyeva',    ism='Nilufar',  lavozim='штат', bino='A' WHERE id=109;
UPDATE oqituvchilar SET familiya='Shodmonov',   ism='Davron',   lavozim='штат', bino='A' WHERE id=108;
UPDATE oqituvchilar SET familiya='Djumayev',    ism='Sindor',   lavozim='штат', bino='A' WHERE id=111;
UPDATE oqituvchilar SET familiya='Yuldoshev',   ism='Aziz',     lavozim='штат', bino='A' WHERE id=116;
UPDATE oqituvchilar SET familiya='Normatova',   ism='Yulduz',   lavozim='штат', bino='A' WHERE id=119;
UPDATE oqituvchilar SET familiya='Axmedjanova', ism='Zarina',   lavozim='штат', bino='A' WHERE id=117;
UPDATE oqituvchilar SET familiya='Shokirov',    ism='Farrux',   lavozim='штат', bino='A' WHERE id=121;

-- Ichki o'rindosh (faqat ichki, shtatda yo'q)
UPDATE oqituvchilar SET familiya='Jiyanov',     ism='Oybek',    lavozim='ички', bino='A' WHERE id=113;
UPDATE oqituvchilar SET familiya='Mamanazarov', ism='Baxrom',   lavozim='ички', bino='A' WHERE id=120;
UPDATE oqituvchilar SET familiya='Toshniyozov', ism='Farrux',   lavozim='ички', bino='A' WHERE id=122;

-- Ichki o'rindosh (YANGI)
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, bino, faol, lavozim) VALUES
  (9, 'Usmonov',      'Asliddin', 'A', TRUE, 'ички'),
  (9, 'Muhammadiyev', 'Bekzod',   'A', TRUE, 'ички');

-- Tashqi o'rindosh: id=110 allaqachon bor (Musinov S.)
UPDATE oqituvchilar SET familiya='Musinov', ism='Sobir', lavozim='ташки', bino='A' WHERE id=110;

-- Tashqi o'rindosh (YANGI)
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, bino, faol, lavozim) VALUES
  (9, 'Raxmatov', 'Inomjon', 'A', TRUE, 'ташки');

-- ════════════════════════════════════════════════════════
-- 6-QADAM: AXBOROT XAVFSIZLIGI (kafedra_id=10)
-- ════════════════════════════════════════════════════════

-- Asosiy (штат)
UPDATE oqituvchilar SET familiya='Zainalov',  ism='Nodir',   lavozim='штат', bino='A' WHERE id=123;
UPDATE oqituvchilar SET familiya='Vafoyev',   ism='Mirabid', lavozim='штат', bino='A' WHERE id=126;
UPDATE oqituvchilar SET familiya='Sharipova', ism='Umida',   lavozim='штат', bino='A' WHERE id=127;
UPDATE oqituvchilar SET familiya='Nishonova', ism='Maftuna', lavozim='штат', bino='A' WHERE id=134;
UPDATE oqituvchilar SET familiya='Kiyamov',   ism='Jasur',   lavozim='штат', bino='A' WHERE id=132;

-- Ichki o'rindosh (faqat ichki)
UPDATE oqituvchilar SET familiya='Mavlonov',  ism='Obidjon', lavozim='ички', bino='A' WHERE id=133;

-- Tashqi o'rindosh (hammasi allaqachon bor)
UPDATE oqituvchilar SET familiya='Bekmurodov',   ism='Ulug''bek',  lavozim='ташки', bino='A' WHERE id=124;
UPDATE oqituvchilar SET familiya='Safarov',      ism='Rustam',     lavozim='ташки', bino='A' WHERE id=125;
UPDATE oqituvchilar SET familiya='Nasriddinova', ism='Parvina',    lavozim='ташки', bino='A' WHERE id=128;
UPDATE oqituvchilar SET familiya='Shakarov',     ism='Asliddin',   lavozim='ташки', bino='A' WHERE id=129;
UPDATE oqituvchilar SET familiya='Saidmurodov',  ism='Muzaffar',   lavozim='ташки', bino='A' WHERE id=130;
UPDATE oqituvchilar SET familiya='Xasanov',      ism='Kamol',      lavozim='ташки', bino='A' WHERE id=131;

-- ════════════════════════════════════════════════════════
-- 7-QADAM: TEKSHIRISH
-- ════════════════════════════════════════════════════════

-- 1. Kafedralar bino bo'yicha
SELECT nomi, bino FROM kafedralar ORDER BY bino, nomi;

-- 2. Har kafedrada nechta o'qituvchi
SELECT k.nomi, k.bino, COUNT(o.id) as soni
FROM kafedralar k
LEFT JOIN oqituvchilar o ON o.kafedra_id = k.id AND o.faol = TRUE
GROUP BY k.id, k.nomi, k.bino
ORDER BY k.bino, k.nomi;

-- 3. A-bino o'qituvchilar (lavozim bilan)
SELECT o.id, o.familiya, o.ism, o.lavozim, k.nomi AS kafedra
FROM oqituvchilar o
JOIN kafedralar k ON k.id = o.kafedra_id
WHERE k.bino = 'A' AND o.faol = TRUE
ORDER BY k.nomi, o.lavozim, o.familiya;
