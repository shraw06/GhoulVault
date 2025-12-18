begin;

create database if not exists tokyo_ghoul;
use tokyo_ghoul;

create table if not exists Kagune (
    id int primary key auto_increment,
    rc enum('ukaku', 'kokaku', 'rinkaku', 'bikaku') not null,
    kakuja_level int
);

create table if not exists Ward (
    id int primary key auto_increment,
    name text not null,
    boundary text not null,
    number int not null,
    city text not null,
    unique (number, city)
);

create table if not exists Report (
    id integer primary key auto_increment,
    date date not null unique,
    text text not null
);

create table if not exists Ghoul (
    id int primary key auto_increment,
    name text not null,
    gender enum('m', 'f', 'o') not null,
    rc_level int not null,
    birth_date date not null,
    age int not null,
    deceased boolean not null default false,
    Ward_id int not null references Ward(id) on update cascade on delete cascade,
    Kagune_id int not null unique references Kagune(id) on update cascade on delete cascade
);

DELIMITER //

-- using a trigger because generated columns do not allow using
-- current_date (no fun allowed)
-- 
create trigger Ghoul_SetAge
before insert or update on Ghoul
for each row begin
    set new.age = timestampdiff(year, new.birth_date, curdate());
    if new.age < 0 then
        set new.age = 0;
    end if;
end //

DELIMITER ;

create table if not exists Rating (
    ghoul_id int not null references Ghoul(id) on update cascade on delete cascade,
    rating enum('S', 'S+', 'S-', 'SS', 'SS+', 'SS-', 'SSS', 'A', 'A+', 'A-', 'B', 'B+', 'B-', 'C') not null,
    primary key (ghoul_id, rating)
);

create table if not exists Human (
    id int primary key auto_increment,
    name text not null,
    gender enum('m', 'f', 'o') not null,
    rc_level int not null,
    birth_date date not null,
    age int not null,
    deceased boolean not null default false
);

DELIMITER //

-- using a trigger because generated columns do not allow using
-- current_date (no fun allowed)
-- 
create trigger Human_SetAge
before insert or update on Human
for each row begin
    set new.age = timestampdiff(year, new.birth_date, curdate());
    if new.age < 0 then
        set new.age = 0;
    end if;
end //

DELIMITER ;

create table if not exists Investigator (
    id int primary key auto_increment references Human(id) on update cascade on delete cascade,
    rank enum('special', 'associate', 'first', '1', '2', '3') not null,
    is_senior boolean not null default false,
    city text not null,
    number int not null,
    check (
        (is_senior = false and rank in ('1', '2', '3'))
      or
        (is_senior = true and not (rank in ('1', '2', '3')))
    )
);

create table if not exists Quinque (
    id int primary key auto_increment,
    rating enum('S', 'S+', 'S-', 'SS', 'SS+', 'SS-', 'SSS', 'A', 'A+', 'A-', 'B', 'B+', 'B-', 'C') not null,
    name text not null,
    owner_id int not null references Investigator(id) on update cascade on delete cascade,
    kagune_id int not null unique references Kagune(id) on update cascade on delete cascade
);

create table if not exists GhoulMurder (
    Murderer int not null references Ghoul(id) on update cascade on delete cascade,
    Victim int not null unique references Human(id) on update cascade on delete cascade,
    Ward int not null references Ward(id) on update cascade on delete cascade,
    time timestamp not null,
    primary key (Murderer, Victim, time)
);

DELIMITER //

CREATE TRIGGER After_GhoulMurder_Insert
AFTER INSERT ON GhoulMurder
FOR EACH ROW
BEGIN
    UPDATE Human SET deceased = TRUE WHERE id = NEW.Victim;
END; //

DELIMITER ;

create table if not exists QuinqueUpgrades (
    Quinque int not null references Quinque(id) on update cascade on delete cascade,
    Investigator int not null references Investigator(id) on update cascade on delete cascade,
    Kagune int not null unique references Kagune(id) on update cascade on delete cascade,
    primary key (Quinque, Kagune)
);

DELIMITER //

CREATE TRIGGER After_QuinqueUpgrade_Insert
AFTER INSERT ON QuinqueUpgrades
FOR EACH ROW
BEGIN
    -- This trigger updates the kakuja level of a Quinque's primary Kagune
    -- if it is upgraded with a Kagune that has a higher kakuja level.

    DECLARE original_kagune_id INT;
    DECLARE original_kakuja_level INT;
    DECLARE new_kakuja_level INT;

    -- 1. Find the original Kagune ID associated with the Quinque being upgraded.
    SELECT kagune_id INTO original_kagune_id
    FROM Quinque
    WHERE id = NEW.Quinque;

    -- 2. Get the kakuja level of the Quinque's original Kagune.
    --    COALESCE is used to treat a NULL kakuja_level as 0 for comparison.
    SELECT COALESCE(kakuja_level, 0) INTO original_kakuja_level
    FROM Kagune
    WHERE id = original_kagune_id;

    -- 3. Get the kakuja level of the new Kagune used for the upgrade.
    SELECT COALESCE(kakuja_level, 0) INTO new_kakuja_level
    FROM Kagune
    WHERE id = NEW.Kagune;

    -- 4. Compare the kakuja levels. If the new one is higher,
    --    update the kakuja level of the Quinque's original Kagune.
    IF new_kakuja_level > original_kakuja_level THEN
        UPDATE Kagune
        SET kakuja_level = new_kakuja_level
        WHERE id = original_kagune_id;
    END IF;
END; //

DELIMITER ;

create table if not exists Killing (
    investigator_id int not null references Investigator(id) on update cascade on delete cascade,
    ghoul_id int not null primary key references Ghoul(id) on update cascade on delete cascade,
    quinque_id int not null references Quinque(id) on update cascade on delete cascade,
    ward_id int not null references Ward(id) on update cascade on delete cascade
);

DELIMITER //

CREATE TRIGGER After_Killing_Insert
AFTER INSERT ON Killing
FOR EACH ROW
BEGIN
    UPDATE Ghoul SET deceased = TRUE WHERE id = NEW.ghoul_id;
END; //

DELIMITER ;

create table if not exists Encounter (
    Senior_id int not null references Investigator(id) on update cascade on delete cascade,
    Junior_id int not null references Investigator(id) on update cascade on delete cascade,
    Ghoul_id int not null references Ghoul(id) on update cascade on delete cascade,
    time timestamp not null,
    death_senior boolean not null,
    death_junior boolean not null,
    death_ghoul boolean not null,
    JuniorQuinque int not null references Quinque(id) on update cascade on delete cascade,
    SeniorQuinque int not null references Quinque(id) on update cascade on delete cascade,
    primary key (Senior_id, Junior_id, Ghoul_id, time)
);

DELIMITER //

CREATE TRIGGER After_Encounter_Insert
AFTER INSERT ON Encounter
FOR EACH ROW
BEGIN
    IF NEW.death_senior = TRUE THEN
        UPDATE Human SET deceased = TRUE WHERE id = NEW.Senior_id;
    END IF;
    IF NEW.death_junior = TRUE THEN
        UPDATE Human SET deceased = TRUE WHERE id = NEW.Junior_id;
    END IF;
    IF NEW.death_ghoul = TRUE THEN
        UPDATE Ghoul SET deceased = TRUE WHERE id = NEW.Ghoul_id;
    END IF;
END; //

DELIMITER ;

create table if not exists OneEyedGhoul (
    HumanPart_id int not null unique references Human(Id) on update cascade on delete cascade,
    HumanParent_id int references Human(Id) on update cascade on delete set null,
    GhoulPart_id int not null unique references Ghoul(Id) on update cascade on delete cascade,
    GhoulParent_id int references Ghoul(Id) on update cascade on delete set null,
    TransplantDonor_id int references Ghoul(Id) on update cascade on delete set null,

    primary key (HumanPart_id, GhoulPart_id)
);

delimiter //

create or replace trigger OneEyedGhoul_Check
before insert or update on OneEyedGhoul
for each row begin
    if not (
        (new.HumanParent_id is not null and new.GhoulParent_id is not null and new.TransplantDonor_id is null)
      or
        (new.HumanParent_id is null and new.GhoulParent_id is null and new.TransplantDonor_id is not null)
    ) then
        signal sqlstate '45000'
        set message_text = 'A one eyed ghoul must either have human&ghoul parents or a transplant donor. Not both/neither.';
    end if;
end; //

delimiter ;

-- From the MySQL docs:  Foreign key referential actions (ON UPDATE, ON DELETE) are
-- prohibited on columns used in CHECK constraints. Likewise, CHECK constraints are
-- prohibited on columns used in foreign key referential actions. [1]
--
-- Thus, we need to use triggers to check the condition on OneEyedGhoul.
--
-- [1]: https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html


create table if not exists Chimera (
    ghoul_id int unique primary key references Ghoul(id) on update cascade on delete cascade,
    parent1_id int references Ghoul(id) on update cascade on delete set null,
    parent2_id int references Ghoul(id) on update cascade on delete set null,
    kagune1_id int not null unique references Kagune(id) on update cascade on delete cascade,
    kagune2_id int not null unique references Kagune(id) on update cascade on delete cascade
);

commit;
