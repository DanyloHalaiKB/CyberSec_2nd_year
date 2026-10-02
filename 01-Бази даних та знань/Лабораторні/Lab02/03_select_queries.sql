-- =====================================================================
-- Лабораторна №2, варіант 7. Скрипт 3: вибірка даних з кожної таблиці
-- (п. 2.4) + приклади запитів із розділу 1.5 методички.
-- =====================================================================
SET NAMES utf8mb4;
USE patrol_police;

-- ---- 2.4. Вибірка з кожної таблиці --------------------------------
SELECT * FROM unit;
SELECT * FROM patrol_officer;
SELECT * FROM vehicle;
SELECT * FROM shift;
SELECT * FROM shift_crew;
SELECT * FROM call_category;
SELECT * FROM incident_call;
SELECT * FROM article;
SELECT * FROM offender;
SELECT * FROM protocol;

-- ---- Приклади із методички (розд. 1.2, 1.4, 1.5) -------------------
SELECT VERSION(), CURRENT_DATE;          -- версія сервера і дата
SELECT DATABASE();                       -- поточна база даних
SHOW TABLES;                             -- список таблиць

-- 1.5.1 Максимальне значення стовпця: найбільша сума штрафу
SELECT MAX(fine_amount) AS max_fine FROM protocol;

-- 1.5.2 Рядок із максимальним значенням: протокол із найбільшим штрафом
SELECT protocol_id, offender_id, fine_amount
FROM protocol
WHERE fine_amount = (SELECT MAX(fine_amount) FROM protocol);

-- та варіант через ORDER BY ... LIMIT 1
SELECT protocol_id, offender_id, fine_amount
FROM protocol
ORDER BY fine_amount DESC
LIMIT 1;

-- 1.5.3 Використання зовнішніх ключів: протоколи з іменами учасників
SELECT p.protocol_id, p.drawn_date, o.full_name AS offender,
       a.article_number, p.fine_amount, p.review_status,
       po.full_name AS officer
FROM protocol p
JOIN offender o        ON o.offender_id = p.offender_id
JOIN article a         ON a.article_id  = p.article_id
JOIN patrol_officer po ON po.officer_id = p.officer_id
ORDER BY p.protocol_id;

-- Склад нарядів: наряд, автомобіль, патрульні та їх ролі
SELECT s.shift_id, s.shift_date, v.plate_number, po.full_name, sc.crew_role
FROM shift s
JOIN vehicle v      ON v.vehicle_id = s.vehicle_id
JOIN shift_crew sc  ON sc.shift_id  = s.shift_id
JOIN patrol_officer po ON po.officer_id = sc.officer_id
ORDER BY s.shift_id, sc.crew_role;

-- Кількість викликів за категоріями
SELECT c.category_name, COUNT(*) AS calls_cnt
FROM incident_call ic
JOIN call_category c ON c.category_id = ic.category_id
GROUP BY c.category_name
ORDER BY calls_cnt DESC;

-- Перевірка цілісності зовнішніх ключів (СУБД має відхилити запис)
-- INSERT INTO shift_crew (shift_id, officer_id, crew_role) VALUES (999, 1, 'старший');
