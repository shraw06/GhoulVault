GET_GHOUL_COUNTS = "select coalesce(count(*), 0) as total, coalesce(sum(case when deceased = false then 1 else 0 end), 0) as alive, coalesce(sum(case when deceased = true then 1 else 0 end), 0) as dead from Ghoul"
GET_HUMAN_COUNTS = "select coalesce(count(*), 0) as total, coalesce(sum(case when deceased = false then 1 else 0 end), 0) as alive, coalesce(sum(case when deceased = true then 1 else 0 end), 0) as dead from Human"
GET_INVESTIGATOR_COUNTS = "select coalesce(count(i.id), 0) as total, coalesce(sum(case when h.deceased = false then 1 else 0 end), 0) as alive, coalesce(sum(case when h.deceased = true then 1 else 0 end), 0) as dead from Investigator i join Human h on i.id = h.id"

WARDS = "select * from Ward"

GHOULS_BASE = """
    select
        g.id, g.name, gender, rc_level, birth_date, age, deceased, w.id as ward_id,
        w.number as ward_number, w.name as ward_name, w.city as ward_city,
        rc as rc_type, kakuja_level, group_concat(r.rating separator '/') as rating
    from Ghoul g inner join Ward w on w.id = g.Ward_id
    inner join Kagune k on k.id = g.Kagune_id
    inner join Rating r on r.ghoul_id = g.id
"""
GHOULS_END = "group by g.id"
GHOULS = GHOULS_BASE + GHOULS_END
GHOUL_BY_ID = GHOULS_BASE + "where g.id = %s " + GHOULS_END
GHOULS_OF_WARD = GHOULS_BASE + "where g.Ward_id = %s " + GHOULS_END
GHOUL_CHIMERA = """
    select
        parent1_id, p1.name as parent1_name, p1.gender as parent1_gender, p1.deceased as parent1_deceased,
        parent2_id, p2.name as parent2_name, p2.gender as parent2_gender, p2.deceased as parent2_deceased,
        k1.rc as kagune1_rc, k1.kakuja_level as kagune1_kakuja_level,
        k2.rc as kagune2_rc, k2.kakuja_level as kagune2_kakuja_level
    from Chimera c inner join Ghoul g on g.id = ghoul_id
    left join Ghoul p1 on p1.id = parent1_id
    left join Ghoul p2 on p2.id = parent2_id
    left join Kagune k1 on k1.id = kagune1_id
    left join Kagune k2 on k2.id = kagune2_id
    where g.id = %s
"""
GHOUL_ONE_EYED = """
    SELECT
        oeg.HumanPart_id, h_part.name as human_part_name, h_part.gender as human_part_gender, h_part.deceased as human_part_deceased,
        oeg.HumanParent_id, h_parent.name as human_parent_name, h_parent.gender as human_parent_gender, h_parent.deceased as human_parent_deceased,
        oeg.GhoulPart_id, g_part.name as ghoul_part_name, g_part.gender as ghoul_part_gender, g_part.deceased as ghoul_part_deceased,
        oeg.GhoulParent_id, g_parent.name as ghoul_parent_name, g_parent.gender as ghoul_parent_gender, g_parent.deceased as ghoul_parent_deceased,
        oeg.TransplantDonor_id, td.name as transplant_donor_name, td.gender as transplant_donor_gender, td.deceased as transplant_donor_deceased
    FROM OneEyedGhoul oeg
    LEFT JOIN Human h_part ON oeg.HumanPart_id = h_part.id
    LEFT JOIN Human h_parent ON oeg.HumanParent_id = h_parent.id
    LEFT JOIN Ghoul g_part ON oeg.GhoulPart_id = g_part.id
    LEFT JOIN Ghoul g_parent ON oeg.GhoulParent_id = g_parent.id
    LEFT JOIN Ghoul td ON oeg.TransplantDonor_id = td.id
    WHERE oeg.GhoulPart_id = %s
"""
GHOUL_MURDERS = """
    select
        h.name, h.age, h.gender, m.time, m.Victim,
        exists(select 1 from Investigator where id = h.id) as is_investigator,
        w.id as ward_id, w.number as ward_number, w.name as ward_name, w.city as ward_city                
    from GhoulMurder m
    inner join Human h on h.id = Victim
    inner join Ward w on m.Ward = w.id
    where Murderer = %s
"""
GHOUL_ENCOUNTERS = """
    select seniorh.name as senior_name, senior.rank as senior_rank, death_senior, Senior_id,
           seniorq.name as senior_quinque_name, seniorq.rating as senior_quinque_rating, SeniorQuinque,
           juniorh.name as junior_name, junior.rank as junior_rank, death_junior, Junior_id,
           juniorq.name as junior_quinque_name, juniorq.rating as junior_quinque_rating, JuniorQuinque,
           death_ghoul, time
    from Encounter
    inner join Investigator senior on senior.id = Senior_id
    inner join Human seniorh on seniorh.id = Senior_id
    inner join Quinque seniorq on seniorq.id = SeniorQuinque
    inner join Investigator junior on junior.id = junior_id
    inner join Human juniorh on juniorh.id = junior_id
    inner join Quinque juniorq on juniorq.id = JuniorQuinque
    where Ghoul_id = %s
"""
GHOUL_KILLER = """
    select investigator_id, ih.name, i.rank, q.name as quinque_name, q.rating as quinque_rating, ward_id, quinque_id
    from Killing inner join Investigator i on i.id = investigator_id
    inner join Human ih on ih.id = i.id
    inner join Quinque q on q.id = quinque_id where ghoul_id = %s
"""

UPDATE_GHOUL = "update Ghoul set name = %s, gender = %s, birth_date = %s, Ward_id = %s where id = %s"
UPDATE_GHOUL_KAGUNE = "update Kagune set rc = %s where id = (select Kagune_id from Ghoul where id = %s)"

INSERT_WARD = (
    "INSERT INTO Ward (name, boundary, number, city) VALUES (%s, %s, %s, %s)"
)

INVESTIGATORS = """
    select i.id, h.name, h.gender, h.rc_level, h.birth_date, h.age, h.deceased,
           i.rank, i.is_senior, i.city, i.number
    from Investigator i
    join Human h on i.id = h.id
    order by i.id
"""

INVESTIGATOR_BY_ID = """
    select i.id, h.name, h.gender, h.rc_level, h.birth_date, h.age, h.deceased,
           i.rank, i.is_senior, i.city, i.number
    from Investigator i
    join Human h on i.id = h.id
    where i.id = %s
"""

INVESTIGATOR_QUINQUES = """
    select id, rating, name from Quinque where owner_id = %s
"""

INVESTIGATOR_ENCOUNTERS = """
    select e.Senior_id, es.name as senior_name, sen.rank as senior_rank, e.Junior_id, ej.name as junior_name, jun.rank as junior_rank,
           e.Ghoul_id, g.name as ghoul_name, e.time,
           e.death_senior, e.death_junior, e.death_ghoul,
           qs.name as senior_quinque, qj.name as junior_quinque,
           qs.rating as senior_quinque_rating, qj.rating as junior_quinque_rating,
           qs.id as senior_quinque_id, qj.id as junior_quinque_id
    from Encounter e
    join Investigator sen on e.Senior_id = sen.id
    join Human es on sen.id = es.id
    join Investigator jun on e.Junior_id = jun.id
    join Human ej on jun.id = ej.id
    join Ghoul g on e.Ghoul_id = g.id
    join Quinque qs on e.SeniorQuinque = qs.id
    join Quinque qj on e.JuniorQuinque = qj.id
    where e.Senior_id = %s or e.Junior_id = %s
    order by e.time desc
"""

INVESTIGATOR_KILLINGS = """
    select k.ghoul_id, g.name as ghoul_name, k.quinque_id, q.name as quinque_name, q.rating as quinque_rating,
           w.name as ward_name, w.number as ward_number, w.city as ward_city
    from Killing k
    join Ghoul g on k.ghoul_id = g.id
    join Quinque q on k.quinque_id = q.id
    join Ward w on k.ward_id = w.id
    where k.investigator_id = %s
"""

HUMAN_KILLER = """
    SELECT
        g.id as ghoul_id,
        g.name as ghoul_name,
        gm.time,
        group_concat(r.rating separator '/') as rating
    FROM GhoulMurder gm
    JOIN Ghoul g ON gm.Murderer = g.id
    JOIN Rating r on r.ghoul_id = g.id
    WHERE gm.Victim = %s
    GROUP BY g.id, gm.time
"""

HUMANS = """
    select id, name, gender, rc_level, birth_date, age, deceased
    from Human
    order by id
"""

HUMAN_BY_ID = """
    select id, name, gender, rc_level, birth_date, age, deceased,
        exists(select 1 from Investigator i where i.id = h.id) as is_investigator
    from Human h
    where id = %s
"""

QUINQUES = """
    select q.id, q.rating, q.name, q.owner_id, i.rank, h.name as investigator_name,
           k.rc, k.kakuja_level
    from Quinque q
    join Investigator i on q.owner_id = i.id
    join Human h on i.id = h.id
    join Kagune k on q.kagune_id = k.id
    order by q.id
"""

QUINQUE_BY_ID = """
    select q.id, q.rating, q.name, q.owner_id, i.rank, h.name as investigator_name,
           k.rc, k.kakuja_level
    from Quinque q
    join Investigator i on q.owner_id = i.id
    join Human h on i.id = h.id
    join Kagune k on q.kagune_id = k.id
    where q.id = %s
"""

QUINQUE_UPGRADES = """
    select qu.Quinque, qu.Investigator, qu.Kagune, k.rc, k.kakuja_level,
           h.name as investigator_name
    from QuinqueUpgrades qu
    join Kagune k on qu.Kagune = k.id
    join Investigator i on qu.Investigator = i.id
    join Human h on i.id = h.id
    where qu.Quinque = %s
"""

REPORTS = """
    select id, date, text from Report order by date desc
"""

REPORT_BY_ID = """
    select id, date, text from Report where id = %s
"""

MURDERS = """
    select gm.Murderer, g.name as murderer_name, gm.Victim, h.name as victim_name,
           w.number as ward_number, w.name as ward_name, gm.time
    from GhoulMurder gm
    join Ghoul g on gm.Murderer = g.id
    join Human h on gm.Victim = h.id
    join Ward w on gm.Ward = w.id
    order by gm.time desc
"""

MURDER_BY_ID = """
    select gm.Murderer, g.name as murderer_name, gm.Victim, h.name as victim_name,
           w.number as ward_number, w.name as ward_name, w.city as ward_city, gm.time
    from GhoulMurder gm
    join Ghoul g on gm.Murderer = g.id
    join Human h on gm.Victim = h.id
    join Ward w on gm.Ward = w.id
    where gm.Murderer = %s and gm.Victim = %s
"""

ENCOUNTERS = """
    select e.Senior_id, es.name as senior_name, e.Junior_id, ej.name as junior_name,
           e.Ghoul_id, g.name as ghoul_name, e.time,
           e.death_senior, e.death_junior, e.death_ghoul,
           qs.name as senior_quinque, qj.name as junior_quinque
    from Encounter e
    join Investigator sen on e.Senior_id = sen.id
    join Human es on sen.id = es.id
    join Investigator jun on e.Junior_id = jun.id
    join Human ej on jun.id = ej.id
    join Ghoul g on e.Ghoul_id = g.id
    join Quinque qs on e.SeniorQuinque = qs.id
    join Quinque qj on e.JuniorQuinque = qj.id
    order by e.time desc
"""

ENCOUNTER_BY_ID = """
    select e.Senior_id, es.name as senior_name, e.Junior_id, ej.name as junior_name,
           e.Ghoul_id, g.name as ghoul_name, e.time,
           e.death_senior, e.death_junior, e.death_ghoul,
           qs.name as senior_quinque, qj.name as junior_quinque
    from Encounter e
    join Investigator sen on e.Senior_id = sen.id
    join Human es on sen.id = es.id
    join Investigator jun on e.Junior_id = jun.id
    join Human ej on jun.id = ej.id
    join Ghoul g on e.Ghoul_id = g.id
    join Quinque qs on e.SeniorQuinque = qs.id
    join Quinque qj on e.JuniorQuinque = qj.id
    where e.Senior_id = %s and e.Junior_id = %s and e.Ghoul_id = %s and e.time = %s
"""

KILLINGS = """
    select k.investigator_id, h.name as investigator_name, k.ghoul_id, g.name as ghoul_name,
           k.quinque_id, q.name as quinque_name, k.ward_id, w.number as ward_number, w.name as ward_name
    from Killing k
    join Investigator i on k.investigator_id = i.id
    join Human h on i.id = h.id
    join Ghoul g on k.ghoul_id = g.id
    join Quinque q on k.quinque_id = q.id
    join Ward w on k.ward_id = w.id
    order by k.investigator_id desc
"""

KILLING_BY_GHOUL = """
    select k.investigator_id, h.name as investigator_name, k.ghoul_id, g.name as ghoul_name,
           k.quinque_id, q.name as quinque_name, k.ward_id, w.number as ward_number, w.name as ward_name
    from Killing k
    join Investigator i on k.investigator_id = i.id
    join Human h on i.id = h.id
    join Ghoul g on k.ghoul_id = g.id
    join Quinque q on k.quinque_id = q.id
    join Ward w on k.ward_id = w.id
    where k.ghoul_id = %s
"""

INSERT_MURDER = "INSERT INTO GhoulMurder (Murderer, Victim, Ward, time) VALUES (%s, %s, %s, %s)"

INSERT_ENCOUNTER = "INSERT INTO Encounter (Senior_id, Junior_id, Ghoul_id, time, death_senior, death_junior, death_ghoul, JuniorQuinque, SeniorQuinque) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

INSERT_KILLING = "INSERT INTO Killing (investigator_id, ghoul_id, quinque_id, ward_id) VALUES (%s, %s, %s, %s)"

DELETE_REPORT = "DELETE FROM Report WHERE id = %s"

UPDATE_QUINQUE_OWNER = "UPDATE Quinque SET owner_id = %s WHERE id = %s"

DECEASED_GHOULS_FOR_QUINQUE_UPGRADE = """
    select
        k.id, k.rc, k.kakuja_level,
        coalesce(g.name, cg.name, 'No Ghoul') as ghoul_name
    from Kagune k
    left join Ghoul g on k.id = g.Kagune_id
    left join Chimera c on k.id = c.kagune1_id or k.id = c.kagune2_id
    left join Ghoul cg on c.ghoul_id = cg.id
    left join QuinqueUpgrades qu on k.id = qu.Kagune
    where qu.Kagune is null and (
        (g.id is not null and g.deceased = true)
        or (cg.id is not null and cg.deceased = true)
        or (g.id is null and c.ghoul_id is null)
    )
"""

INSERT_QUINQUE_UPGRADE = "INSERT INTO QuinqueUpgrades (Quinque, Investigator, Kagune) VALUES (%s, %s, %s)"

INSERT_REPORT = "INSERT INTO Report (date, text) VALUES (%s, %s)"
