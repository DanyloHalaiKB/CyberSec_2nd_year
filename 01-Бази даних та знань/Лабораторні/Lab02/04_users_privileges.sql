-- =====================================================================
-- Лабораторна №2, варіант 7. Скрипт 4: облікові записи й привілеї
-- (розд. 1.6 методички: принцип мінімально необхідних прав).
-- Виконувати від імені root.
-- =====================================================================
SET NAMES utf8mb4;

-- Зміна пароля root (виконати один раз; значення пароля замініть своїм):
--   ALTER USER 'root'@'localhost' IDENTIFIED BY 'НОВИЙ_ПАРОЛЬ';
-- або для поточного користувача:
--   SET PASSWORD = 'НОВИЙ_ПАРОЛЬ';

-- Прибираємо облікові записи, якщо скрипт запускається повторно
DROP USER IF EXISTS 'patrol_app'@'localhost';
DROP USER IF EXISTS 'patrol_reader'@'localhost';

-- 1) Обліковий запис застосунку: може змінювати дані лише у БД patrol_police
CREATE USER 'patrol_app'@'localhost' IDENTIFIED BY 'Lab2_app_pwd!';
GRANT SELECT, INSERT, UPDATE, DELETE ON patrol_police.* TO 'patrol_app'@'localhost';

-- 2) Обліковий запис лише для читання (наприклад, для контролюючих осіб)
CREATE USER 'patrol_reader'@'localhost' IDENTIFIED BY 'Lab2_read_pwd!';
GRANT SELECT ON patrol_police.* TO 'patrol_reader'@'localhost';

-- Перевіряємо, хто і які права має (SHOW GRANTS)
SHOW GRANTS FOR 'patrol_app'@'localhost';
SHOW GRANTS FOR 'patrol_reader'@'localhost';

-- Забираємо зайве право (REVOKE): застосунок не має видаляти дані
REVOKE DELETE ON patrol_police.* FROM 'patrol_app'@'localhost';
SHOW GRANTS FOR 'patrol_app'@'localhost';

-- Список облікових записів сервера (тільки root має доступ до mysql.user)
SELECT user, host FROM mysql.user ORDER BY user;
