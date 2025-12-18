use tokyo_ghoul;

begin;
 
-- First, insert Wards (Tokyo Ghoul anime wards)
INSERT INTO Ward (id, name, boundary, number, city) VALUES
(1, 'Chiyoda', 'Northwest Tokyo', 1, 'Tokyo'),
(2, 'Chuo', 'North Tokyo', 2, 'Tokyo'),
(3, 'Minato', 'North Tokyo', 3, 'Tokyo'),
(4, 'Shinjuku', 'South Tokyo', 4, 'Tokyo'),
(5, 'Bunkyo', 'South Tokyo', 5, 'Tokyo'),
(6, 'Taito', 'Southwest Tokyo', 6, 'Tokyo'),
(7, 'Sumida', 'Central Tokyo', 7, 'Tokyo'),
(8, 'Koto', 'West Central Tokyo', 8, 'Tokyo'),
(9, 'Shinagawa', 'Northwest Tokyo', 9, 'Tokyo'),
(10, 'Meguro', 'East Tokyo', 10, 'Tokyo'),
(11, 'Ota', 'Northeast Tokyo', 11, 'Tokyo'),
(12, 'Setagaya', 'Southwest Tokyo', 12, 'Tokyo'),
(13, 'Shibuya', 'Central Tokyo', 13, 'Tokyo'),
(14, 'Nakano', 'Central Tokyo', 14, 'Tokyo'),
(15, 'Suginami', 'East Central Tokyo', 15, 'Tokyo'),
(16, 'Toshima', 'North Central Tokyo', 16, 'Tokyo'),
(17, 'Kita', 'East Tokyo', 17, 'Tokyo'),
(18, 'Arakawa', 'East Tokyo', 18, 'Tokyo'),
(19, 'Itabashi', 'Northeast Tokyo', 19, 'Tokyo'),
(20, 'Nerima', 'Northwest Tokyo', 20, 'Tokyo'),
(21, 'Adachi', 'West Tokyo', 21, 'Tokyo'),
(22, 'Ka', 'West Tokyo', 22, 'Tokyo'),
(23, 'Musashino', 'West Tokyo', 23, 'Tokyo'),
(24, 'Underground', 'Tokyo', 24, 'Tokyo');

-- 2. CREATE KAGUNES (Sacs)
-- IDs will auto-increment from 1 to 26 based on this order
INSERT INTO Kagune (id, rc, kakuja_level) VALUES 
(1, 'rinkaku', 0), -- Rize (Donor)
(2, 'ukaku', 0),   -- Touka
(3, 'rinkaku', 1), -- Jason (Yamori)
(4, 'kokaku', 0),  -- Hinami Primary
(5, 'rinkaku', 0), -- Hinami Secondary
(6, 'kokaku', 0),  -- Ryoko (Mom)
(7, 'rinkaku', 0), -- Asaki (Dad)
(8, 'rinkaku', 1), -- Kaneki (Ghoul side)
(9, 'rinkaku', 0), -- For Quinque: Fueguchi 1
(10, 'kokaku', 0),  -- For Quinque: Fueguchi 2
(11, 'rinkaku', 1), -- For Quinque: 13s Jason
(12, 'ukaku', 2),   -- Yoshimura (Manager)
(13, 'ukaku', 3),   -- Eto (Owl)
(14, 'ukaku', 0),   -- Yomo
(15, 'bikaku', 0),  -- Nishiki
(16, 'kokaku', 0),  -- Tsukiyama
(17, 'rinkaku', 0), -- Uta
(18, 'ukaku', 0),   -- Ayato
(19, 'bikaku', 1),  -- Tatara
(20, 'kokaku', 0),  -- Naki
(21, 'rinkaku', 1), -- Noro
(22, 'bikaku', 0),  -- Koma (Ape)
(23, 'ukaku', 0),   -- Irimi (Dog)
(24, 'kokaku', 1),  -- For Quinque: IXA
(25, 'ukaku', 1),   -- For Quinque: Narukami
(26, 'kokaku', 1),  -- For Quinque: Arata Proto
(27, 'kokaku', 1),  -- Extra Kagune
(28, 'ukaku', 2),
(29, 'rinkaku', 1); 

-- 3. CREATE HUMANS
-- IDs 1 to 10
INSERT INTO Human (id, name, gender, rc_level, birth_date, deceased) VALUES 
(1, 'Ken Kaneki', 'm', 170, '1994-12-20', false),       -- 1
(2, 'Kureo Mado', 'm', 200, '1960-01-24', true),        -- 2
(3, 'Koutarou Amon', 'm', 500, '1987-04-07', false),    -- 3
(4, 'Juuzou Suzuya', 'o', 200, '1995-06-08', false),    -- 4
(5, 'Hideyoshi Nagachika', 'm', 150, '1994-06-10', false), -- 5
(6, 'Ukina', 'f', 200, '1965-01-01', true),             -- 6 (Eto's Mom)
(7, 'Eto Yoshimura', 'f', 50, '1993-12-29', false),     -- 7 (Human disguise)
(8, 'Kishou Arima', 'm', 10, '1983-12-20', false),      -- 8
(9, 'Yukinori Shinohara', 'm', 50, '1977-05-10', false),-- 9
(10, 'Akira Mado', 'f', 100, '1994-06-06', false);       -- 10

-- 4. CREATE GHOULS
-- IDs 1 to 19
INSERT INTO Ghoul (id, name, gender, rc_level, birth_date, deceased, Ward_id, Kagune_id) VALUES 
(1, 'Rize Kamishiro', 'f', 2300, '1994-10-01', true, 1, 1),
(2, 'Touka Kirishima', 'f', 1800, '1994-07-01', false, 1, 2),
(3, 'Yakumo Oomori', 'm', 5000, '1985-03-15', true, 3, 3),
(4, 'Ryoko Fueguchi', 'f', 1200, '1975-01-01', true, 1, 6),
(5, 'Asaki Fueguchi', 'm', 1400, '1975-01-01', true, 1, 7),
(6, 'Hinami Fueguchi', 'f', 3800, '2004-05-21', false, 1, 4),
(7, 'Ken Kaneki', 'm', 2700, '1993-02-20', false, 1, 8),
(8, 'Yoshimura', 'm', 8000, '1960-06-20', false, 1, 12),
(9, 'Renji Yomo', 'm', 2500, '1983-07-09', false, 4, 14),
(10, 'Nishiki Nishio', 'm', 1900, '1994-02-04', false, 1, 15),
(11, 'Enji Koma', 'm', 2600, '1980-03-24', false, 1, 22),
(12, 'Kaya Irimi', 'f', 2600, '1980-06-09', false, 1, 23),
(13, 'Shuu Tsukiyama', 'm', 2400, '1992-03-03', false, 1, 16),
(14, 'Uta', 'm', 3500, '1983-12-02', false, 4, 17),
(15, 'Eto', 'f', 9000, '1993-12-29', false, 5, 13),
(16, 'Ayato Kirishima', 'm', 2800, '1997-07-04', false, 2, 18),
(17, 'Tatara', 'm', 5500, '1980-01-01', false, 2, 19),
(18, 'Naki', 'm', 2200, '1990-01-28', true, 2, 20),
(19, 'Noro', 'm', 6000, '1983-03-12', true, 2, 21);

-- 5. ASSIGN RATINGS
INSERT INTO Rating (ghoul_id, rating) VALUES 
(1, 'S'), (2, 'S'), (3, 'S+'), (4, 'A'), (5, 'A'), (6, 'SS'), (7, 'SS'), 
(8, 'SSS'), (9, 'SS'), (10, 'S'), (11, 'SS'), (12, 'SS'), (13, 'S+'), 
(14, 'SS'), (15, 'SSS'), (16, 'SS'), (17, 'SS+'), (18, 'S'), (19, 'SS+');

-- 6. SPECIAL LINKING TABLES (One-Eyed & Chimera)
-- Kaneki (Transplant from Rize) & Eto (Natural Born)
INSERT INTO OneEyedGhoul (HumanPart_id, HumanParent_id, GhoulPart_id, GhoulParent_id, TransplantDonor_id) VALUES 
(1, NULL, 7, NULL, 1),  -- Kaneki
(7, 6, 15, 8, NULL);    -- Eto (Mom: Ukina, Dad: Yoshimura)

-- Hinami (Chimera)
INSERT INTO Chimera (ghoul_id, parent1_id, parent2_id, kagune1_id, kagune2_id) VALUES 
(6, 4, 5, 4, 5);

-- 7. CREATE INVESTIGATORS
-- Following your schema constraint: Rank 1,2,3 = Senior(True), Special/First = Senior(False)
INSERT INTO Investigator (id, rank, is_senior, city, number) VALUES 
(2, 'special', true, 'Tokyo', 20),  -- Mado
(3, '1', false, 'Tokyo', 20),       -- Amon
(4, '1', false, 'Tokyo', 13),       -- Suzuya
(8, 'special', true, 'Tokyo', 1), -- Arima
(9, 'special', true, 'Tokyo', 20),-- Shinohara
(10, '2', false, 'Tokyo', 20);      -- Akira

-- 8. CREATE QUINQUES
INSERT INTO Quinque (rating, name, owner_id, kagune_id) VALUES 
('A', 'Fueguchi One', 2, 9),     -- Mado
('S', 'Fueguchi Two', 2, 10),    -- Mado
('S+', '13s Jason', 4, 11),      -- Suzuya
('S+', 'IXA', 8, 24),            -- Arima
('S+', 'Narukami', 8, 25),       -- Arima
('SS', 'Arata Proto', 9, 26);    -- Shinohara

INSERT INTO QuinqueUpgrades (Quinque, Investigator, Kagune) VALUES
(1, 2, 27),   -- Mado upgrades "Fueguchi One"
(3, 4, 28),   -- Suzuya upgrades "13's Jason"
(4, 8, 29);   -- Arima upgrades "IXA"

-- 10. REPORTS
INSERT INTO Report (id, date, text) VALUES
(1, '2014-01-01', 'Increased ghoul activity observed in Ward 1.'),
(2, '2014-03-11', 'Aogiri Tree presence expanding across central wards.'),
(3, '2014-06-20', 'Unidentified SSS-class ghoul spotted near Ward 4.');

-- 11. GHOUL MURDERS
-- Constraint: Victim (Human id) must be unique.
INSERT INTO GhoulMurder (Murderer, Victim, Ward, time) VALUES
(3, 2, 3, '2012-09-10 11:12:13'),   -- Jason kills Kureo Mado (anime canon)
(15, 6, 5, '2012-05-04 15:02:01');  -- Eto kills Ukina (backstory canonical)

-- 12. KILLING
-- Constraint: ghoul_id is PRIMARY KEY → each ghoul killed once.
-- Investigators must own the quinque.
INSERT INTO Killing (investigator_id, ghoul_id, quinque_id, ward_id) VALUES
(2, 4, 1, 1),   -- Mado kills Ryoko (using Fueguchi One)
(4, 3, 3, 3),   -- Suzuya kills Jason (using 13’s Jason)
(8, 19, 4, 2);  -- Arima kills Noro (non-canon but consistent and valid)

-- 13. ENCOUNTERS
-- PK = (Senior_id, Junior_id, Ghoul_id, time)
-- Must reference quinques actually owned by investigators.

INSERT INTO Encounter (
    Senior_id, Junior_id, Ghoul_id, time,
    death_senior, death_junior, death_ghoul,
    JuniorQuinque, SeniorQuinque
) VALUES
-- Suzuya + Mado vs Touka (nonfatal)
(4, 2, 2, '2014-02-10 10:00:00',
 false, false, false,
 1, 3), -- Mado uses Quinque 1, Suzuya uses Quinque 3

-- Suzuya + Arima vs Naki (ghoul dies)
(4, 8, 18, '2014-07-18 20:30:00',
 false, false, true,
 4, 3), -- Arima uses IXA (4), Suzuya uses 13’s Jason (3)

-- Suzuya + Shinohara vs Nishiki (nonfatal)
(4, 9, 10, '2014-04-14 15:45:00',
 false, false, false,
 6, 3); -- Shinohara uses Arata Proto (6), Suzuya uses 13’s Jason (3)



commit;
