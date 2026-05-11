CREATE TABLE IF NOT EXISTS foydalanuvchilar (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    ism TEXT NOT NULL,
    familiya TEXT NOT NULL,
    tel_raqam TEXT,
    yaratilgan TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kafedralar (
    id SERIAL PRIMARY KEY,
    nomi TEXT NOT NULL,
    bino TEXT,
    qavat INTEGER,
    xona_raqam INTEGER
);

CREATE TABLE IF NOT EXISTS oqituvchilar (
    id SERIAL PRIMARY KEY,
    kafedra_id INTEGER REFERENCES kafedralar(id),
    ism TEXT NOT NULL,
    familiya TEXT NOT NULL,
    otasining_ismi TEXT,
    tel_raqam TEXT,
    telegram_username TEXT,
    telegram_file_id TEXT,
    xona_raqam INTEGER,
    bino TEXT,
    faol BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dars_jadvali (
    id SERIAL PRIMARY KEY,
    oqituvchi_id INTEGER REFERENCES oqituvchilar(id),
    xona_raqam INTEGER,
    bino TEXT,
    fan_nomi TEXT NOT NULL,
    guruh TEXT,
    kun TEXT CHECK (kun IN ('dushanba','seshanba','chorshanba','payshanba','juma')),
    boshlanish TIME NOT NULL,
    tugash TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS xonalar (
    id SERIAL PRIMARY KEY,
    raqam INTEGER NOT NULL,
    bino TEXT NOT NULL,
    qavat INTEGER NOT NULL,
    band BOOLEAN DEFAULT FALSE,
    band_gacha TEXT,
    dars_id INTEGER REFERENCES dars_jadvali(id)
);

CREATE TABLE IF NOT EXISTS loglar (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT,
    tur TEXT,
    matn TEXT,
    vaqt TIMESTAMP DEFAULT NOW()
);

INSERT INTO kafedralar (nomi) VALUES
('Tillar'),
('Ijtimoiy gumanitar-1'),
('Ijtimoiy gumanitar-2'),
('Tabiiy fanlar'),
('Axborot texnologiyalari'),
('Dasturiy injiniring'),
('Kompyuter tizimlari'),
('Telekommunikatsiya injiniringi'),
('Raqamli va ta''lim texnologiyalari'),
('Axborot xavfsizligi');
