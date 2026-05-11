-- Avval eski ma'lumotlarni tozalash (agar bo'lsa)
TRUNCATE oqituvchilar RESTART IDENTITY CASCADE;
TRUNCATE kafedralar RESTART IDENTITY CASCADE;

INSERT INTO kafedralar (id, nomi) VALUES
  (1,  'Tillar'),
  (2,  'Ijtimoiy gumanitar-1'),
  (3,  'Ijtimoiy gumanitar-2'),
  (4,  'Tabiiy fanlar'),
  (5,  'Axborot texnologiyalari'),
  (6,  'Dasturiy injiniring'),
  (7,  'Kompyuter tizimlari'),
  (8,  'Telekommunikatsiya injiniringi'),
  (9,  'Raqamli va ta''lim texnologiyalari'),
  (10, 'Axborot xavfsizligi');

SELECT setval('kafedralar_id_seq', 10);

-- TILLAR
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (1,'Toirova','D.','+998915389878'),
  (1,'Xotamov','N.','+998911875935'),
  (1,'Raxmatova','S.','+998902129106'),
  (1,'Ibatova','A.','+998906010744'),
  (1,'Toshpulatov','D.','+998906007345'),
  (1,'Narziyeva','G.',NULL),
  (1,'Akramova','M.',NULL);

-- IJTIMOIY GUMANITAR-1
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (2,'Samadov','X.','+998915273808'),
  (2,'Muxammadiyev','X.','+998915252161'),
  (2,'Kubayeva','Sh.','+998937038101'),
  (2,'Mardonov','R.',NULL),
  (2,'Kubayeva','G.E.',NULL),
  (2,'Azimov','Sh.',NULL),
  (2,'Rizoyev','I.',NULL),
  (2,'Shavqiyev','O.',NULL);

-- IJTIMOIY GUMANITAR-2
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (3,'Axmedjanov','A.R.',NULL),
  (3,'Rajabov','O.',NULL),
  (3,'Djulmatova','S.','+998906002660'),
  (3,'Ismoilova','F.','+998979154686'),
  (3,'Abdullayev','J.','+998978949392'),
  (3,'Togayeva','D.',NULL),
  (3,'Baxodirov','B.',NULL),
  (3,'Abdukarimova','M.',NULL),
  (3,'Ibodullayeva','M.',NULL),
  (3,'Latipov','A.','+998979278994'),
  (3,'Qudratova','D.',NULL),
  (3,'Achilov','S.',NULL);

-- TABIIY FANLAR
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (4,'Yaxshibo''yev','M.',NULL),
  (4,'Asrorov','Sh.',NULL),
  (4,'Narzullayev','U.',NULL),
  (4,'Azimov','U.',NULL),
  (4,'Kurbaniyozov','',NULL),
  (4,'Rajabov','J.',NULL),
  (4,'Diyorov','A.',NULL),
  (4,'Holiyarova','F.',NULL),
  (4,'Juraqulov','A.',NULL),
  (4,'Urolov','Sh.',NULL),
  (4,'Ishonkulov','F.',NULL),
  (4,'Dustmurodov','G.',NULL),
  (4,'Indiaminov','R.',NULL),
  (4,'Davronov','B.',NULL),
  (4,'Muminov','',NULL),
  (4,'Latifov','',NULL),
  (4,'Qudratov','H.',NULL),
  (4,'Boboqambarova','G.',NULL),
  (4,'Maxmatqulov','T.',NULL),
  (4,'Nurmanova','M.',NULL),
  (4,'Fozilov','A.',NULL),
  (4,'Ortiqov','',NULL),
  (4,'Maxmudov','F.',NULL);

-- AXBOROT TEXNOLOGIYALARI
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (5,'Xo''jayorov','I.',NULL),
  (5,'Maxmudov','Z.','+998905046851'),
  (5,'Fattayeva','D.',NULL),
  (5,'Isroilov','Sh.','+998979108586'),
  (5,'Raximov','R.','+998974228058'),
  (5,'Abduvaitov','A.','+998937036063'),
  (5,'Ibroximova','Z.','+998937233755'),
  (5,'Abatov','Sh.','+998942422224'),
  (5,'Kudratov','R.',NULL),
  (5,'Primova','X.',NULL),
  (5,'Saidqulov','E.',NULL),
  (5,'Xaqberdiyev','S.',NULL),
  (5,'Nabiyeva','D.',NULL),
  (5,'Mirsadiyev','B.',NULL),
  (5,'Umarov','E.',NULL);

-- DASTURIY INJINIRING
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (6,'Boynazarov','I.','+998905207309'),
  (6,'Qarshiyev','A.B.','+998915493089'),
  (6,'Bobonazarov','A.','+998945310191'),
  (6,'Safarova','G.',NULL),
  (6,'Qayumov','A.','+998933333732'),
  (6,'Maxmudov','R.','+998933542025'),
  (6,'Turkmenova','R.',NULL),
  (6,'Maxkamova','D.',NULL),
  (6,'Mamayev','M.',NULL),
  (6,'Djumayozov','U.',NULL),
  (6,'Maxmidov','Sh.',NULL),
  (6,'Shamsiddinova','N.',NULL),
  (6,'Tursunov','M.',NULL),
  (6,'Raxmonova','R.',NULL),
  (6,'Badalova','M.',NULL);

-- KOMPYUTER TIZIMLARI
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (7,'Abdullayeva','N.',NULL),
  (7,'Abdukarimov','A.','+998955075493'),
  (7,'Kubaev','S.','+998933595858'),
  (7,'Norqulov','A.',NULL),
  (7,'Murtozaeva','U.','+998915415565'),
  (7,'Sattorov','M.','+998979251491'),
  (7,'Mamaraufov','O.',NULL),
  (7,'Qo''chqorov','F.',NULL),
  (7,'Nabiyeva','I.',NULL),
  (7,'Xusanov','K.',NULL),
  (7,'Xamiyev','A.',NULL),
  (7,'Axrorov','M.',NULL);

-- TELEKOMMUNIKATSIYA INJINIRINGI
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (8,'Mirzaqulov','H.','+998945325767'),
  (8,'Jumanov','X.','+998915239593'),
  (8,'Kilichov','J.','+998942992324'),
  (8,'Xotamov','A.','+998905578444'),
  (8,'Bolbekov','M.','+998933327111'),
  (8,'Xidirov','A.','+998902710884'),
  (8,'Nurmurodov','J.','+998932300206'),
  (8,'Jumaboev','T.','+998937285826'),
  (8,'Nizomov','A.',NULL),
  (8,'Urinov','J.',NULL),
  (8,'G''ayratov','Z.',NULL),
  (8,'Xodjayev','M.',NULL),
  (8,'G''aybullayev','A.',NULL),
  (8,'Djurayev','Adil',NULL);

-- RAQAMLI VA TA'LIM TEXNOLOGIYALARI
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (9,'Raxmonov','X.',NULL),
  (9,'Shodmonov','D.','+998933487965'),
  (9,'Ganieva','N.','+998905030085'),
  (9,'Musinov','S.',NULL),
  (9,'Djumaev','S.','+998937252207'),
  (9,'Umarov','A.','+998937230577'),
  (9,'Jiyanov','O.','+998933329487'),
  (9,'Xolyarova','F.','+998915544574'),
  (9,'Irisbaeva','M.',NULL),
  (9,'Yo''ldoshov','A.','+998942840691'),
  (9,'Axmedjanova','Z.','+998915433452'),
  (9,'Narzullaeva','N.',NULL),
  (9,'Normatova','Yu.',NULL),
  (9,'Mamanazarov','B.',NULL),
  (9,'Shokirov','F.',NULL),
  (9,'Toshniyozov','F.',NULL);

-- AXBOROT XAVFSIZLIGI
INSERT INTO oqituvchilar (kafedra_id, familiya, ism, tel_raqam) VALUES
  (10,'Zaynalov','N.',NULL),
  (10,'Bekmurodov','U.','+998933310053'),
  (10,'Safarov','R.',NULL),
  (10,'Vafaev','M.',NULL),
  (10,'Sharipova','U.',NULL),
  (10,'Nasriddinova','P.',NULL),
  (10,'Shakarov','A.',NULL),
  (10,'Saidmurodov','M.',NULL),
  (10,'Xasanov','K.',NULL),
  (10,'Kiyamov','J.',NULL),
  (10,'Mavlonov','O.',NULL),
  (10,'Nishonova','M.',NULL);

-- Tekshirish
SELECT k.nomi, COUNT(o.id) as soni
FROM kafedralar k
LEFT JOIN oqituvchilar o ON o.kafedra_id = k.id
GROUP BY k.id, k.nomi
ORDER BY k.id;
