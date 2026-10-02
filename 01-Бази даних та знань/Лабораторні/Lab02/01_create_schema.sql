-- =====================================================================
-- Лабораторна робота №2, варіант 7
-- БД "Управління патрульної поліції в області" (схема з Лабораторної №1)
-- Скрипт 1: створення бази даних і таблиць (DDL)
-- СУБД: MySQL 8.4, рушій InnoDB (підтримує зовнішні ключі)
-- =====================================================================
SET NAMES utf8mb4;

-- Створюємо базу даних (у Linux імена БД чутливі до регістру, тому
-- всі ідентифікатори пишемо малими літерами латиницею).
DROP DATABASE IF EXISTS patrol_police;
CREATE DATABASE patrol_police
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- Вибір бази робимо в кожному сеансі окремо (команда USE).
USE patrol_police;

-- Таблиці створюємо в порядку "батьківські -> дочірні", щоб зовнішні
-- ключі завжди посилалися на вже існуючі таблиці.

-- R2. Підрозділ
CREATE TABLE unit (
    unit_id       INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_підрозділу',
    unit_name     VARCHAR(100) NOT NULL COMMENT 'Назва підрозділу',
    station_addr  VARCHAR(150) NOT NULL COMMENT 'Адреса дільниці',
    duty_phone    VARCHAR(20)  NOT NULL COMMENT 'Телефон чергової частини',
    PRIMARY KEY (unit_id)
) ENGINE=InnoDB;

-- R1. Патрульний
CREATE TABLE patrol_officer (
    officer_id  INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_патрульного',
    full_name   VARCHAR(100) NOT NULL COMMENT 'ПІБ',
    rank_name   VARCHAR(40)  NOT NULL COMMENT 'Звання',
    birth_date  DATE         NOT NULL COMMENT 'Дата народження',
    phone       VARCHAR(20)  NULL     COMMENT 'Телефон',
    unit_id     INT UNSIGNED NOT NULL COMMENT 'ID_підрозділу (FK)',
    PRIMARY KEY (officer_id),
    CONSTRAINT fk_officer_unit FOREIGN KEY (unit_id) REFERENCES unit (unit_id)
) ENGINE=InnoDB;

-- R3. Автомобіль
CREATE TABLE vehicle (
    vehicle_id    INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_автомобіля',
    plate_number  VARCHAR(12)  NOT NULL COMMENT 'Державний номер',
    brand         VARCHAR(40)  NOT NULL COMMENT 'Марка',
    model         VARCHAR(40)  NOT NULL COMMENT 'Модель',
    year_made     SMALLINT UNSIGNED NOT NULL COMMENT 'Рік випуску',
    unit_id       INT UNSIGNED NOT NULL COMMENT 'ID_підрозділу (FK)',
    PRIMARY KEY (vehicle_id),
    UNIQUE KEY uq_vehicle_plate (plate_number),
    CONSTRAINT chk_vehicle_year CHECK (year_made BETWEEN 1990 AND 2100),
    CONSTRAINT fk_vehicle_unit FOREIGN KEY (unit_id) REFERENCES unit (unit_id)
) ENGINE=InnoDB;

-- R4. Наряд
CREATE TABLE shift (
    shift_id    INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_наряду',
    vehicle_id  INT UNSIGNED NOT NULL COMMENT 'ID_автомобіля (FK)',
    unit_id     INT UNSIGNED NOT NULL COMMENT 'ID_підрозділу (FK)',
    shift_date  DATE         NOT NULL COMMENT 'Дата',
    start_time  TIME         NOT NULL COMMENT 'Час початку',
    end_time    TIME         NOT NULL COMMENT 'Час закінчення',
    PRIMARY KEY (shift_id),
    CONSTRAINT fk_shift_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicle (vehicle_id),
    CONSTRAINT fk_shift_unit    FOREIGN KEY (unit_id)    REFERENCES unit (unit_id)
) ENGINE=InnoDB;

-- R5. Склад наряду
CREATE TABLE shift_crew (
    crew_id     INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_складу',
    shift_id    INT UNSIGNED NOT NULL COMMENT 'ID_наряду (FK)',
    officer_id  INT UNSIGNED NOT NULL COMMENT 'ID_патрульного (FK)',
    crew_role   ENUM('старший','молодший') NOT NULL COMMENT 'Роль у наряді',
    PRIMARY KEY (crew_id),
    CONSTRAINT fk_crew_shift   FOREIGN KEY (shift_id)   REFERENCES shift (shift_id),
    CONSTRAINT fk_crew_officer FOREIGN KEY (officer_id) REFERENCES patrol_officer (officer_id)
) ENGINE=InnoDB;

-- R6. Категорія звернення
CREATE TABLE call_category (
    category_id    INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_категорії',
    category_name  VARCHAR(80)  NOT NULL COMMENT 'Назва категорії',
    description    VARCHAR(255) NULL     COMMENT 'Опис категорії',
    PRIMARY KEY (category_id)
) ENGINE=InnoDB;

-- R7. Виклик (call — зарезервоване слово MySQL, тому таблиця incident_call)
CREATE TABLE incident_call (
    call_id      INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_виклику',
    shift_id     INT UNSIGNED NOT NULL COMMENT 'ID_наряду (FK)',
    category_id  INT UNSIGNED NOT NULL COMMENT 'ID_категорії (FK)',
    call_date    DATE         NOT NULL COMMENT 'Дата',
    call_time    TIME         NOT NULL COMMENT 'Час',
    address      VARCHAR(150) NOT NULL COMMENT 'Адреса',
    description  VARCHAR(255) NULL     COMMENT 'Опис виклику',
    PRIMARY KEY (call_id),
    CONSTRAINT fk_call_shift    FOREIGN KEY (shift_id)    REFERENCES shift (shift_id),
    CONSTRAINT fk_call_category FOREIGN KEY (category_id) REFERENCES call_category (category_id)
) ENGINE=InnoDB;

-- R8. Стаття (КУпАП/ККУ)
CREATE TABLE article (
    article_id      INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_статті',
    article_number  VARCHAR(20)  NOT NULL COMMENT 'Номер статті',
    article_title   VARCHAR(200) NOT NULL COMMENT 'Назва статті',
    fine_min        DECIMAL(10,2) NOT NULL COMMENT 'Штраф (мінімальний), грн',
    fine_max        DECIMAL(10,2) NOT NULL COMMENT 'Штраф (максимальний), грн',
    PRIMARY KEY (article_id),
    CONSTRAINT chk_article_fine CHECK (fine_min >= 0 AND fine_min <= fine_max)
) ENGINE=InnoDB;

-- R9. Порушник
CREATE TABLE offender (
    offender_id      INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_порушника',
    full_name        VARCHAR(100) NOT NULL COMMENT 'ПІБ',
    birth_date       DATE         NOT NULL COMMENT 'Дата народження',
    address          VARCHAR(150) NULL     COMMENT 'Адреса',
    passport_series  CHAR(2)      NOT NULL COMMENT 'Серія паспорта',
    passport_number  CHAR(6)      NOT NULL COMMENT 'Номер паспорта',
    PRIMARY KEY (offender_id),
    UNIQUE KEY uq_offender_passport (passport_series, passport_number)
) ENGINE=InnoDB;

-- R10. Протокол
CREATE TABLE protocol (
    protocol_id    INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID_протоколу',
    call_id        INT UNSIGNED NOT NULL COMMENT 'ID_виклику (FK)',
    officer_id     INT UNSIGNED NOT NULL COMMENT 'ID_патрульного, що склав (FK)',
    article_id     INT UNSIGNED NOT NULL COMMENT 'ID_статті (FK)',
    offender_id    INT UNSIGNED NOT NULL COMMENT 'ID_порушника (FK)',
    drawn_date     DATE         NOT NULL COMMENT 'Дата складання',
    fine_amount    DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Сума штрафу, грн',
    review_status  ENUM('складено','на розгляді','розглянуто','оскаржено')
                   NOT NULL DEFAULT 'складено' COMMENT 'Статус розгляду',
    PRIMARY KEY (protocol_id),
    CONSTRAINT chk_protocol_fine CHECK (fine_amount >= 0),
    CONSTRAINT fk_protocol_call    FOREIGN KEY (call_id)     REFERENCES incident_call (call_id),
    CONSTRAINT fk_protocol_officer FOREIGN KEY (officer_id)  REFERENCES patrol_officer (officer_id),
    CONSTRAINT fk_protocol_article FOREIGN KEY (article_id)  REFERENCES article (article_id),
    CONSTRAINT fk_protocol_offender FOREIGN KEY (offender_id) REFERENCES offender (offender_id)
) ENGINE=InnoDB;

-- Перевірка результату
SHOW TABLES;
DESCRIBE unit;
DESCRIBE patrol_officer;
DESCRIBE vehicle;
DESCRIBE shift;
DESCRIBE shift_crew;
DESCRIBE call_category;
DESCRIBE incident_call;
DESCRIBE article;
DESCRIBE offender;
DESCRIBE protocol;
