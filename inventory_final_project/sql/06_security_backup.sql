USE `Personal_Finance`;

-- =========================================================
-- SECURITY, ROLES, USERS, BACKUP AND ADMINISTRATION NOTES
-- =========================================================

-- 1) ROLES
CREATE ROLE IF NOT EXISTS role_admin;
CREATE ROLE IF NOT EXISTS role_inventory_manager;

GRANT ALL PRIVILEGES ON `Personal_Finance`.* TO role_admin;
GRANT SELECT, INSERT, UPDATE, EXECUTE ON `Personal_Finance`.* TO role_inventory_manager;

-- 2) DEMO USERS
-- Change passwords before presenting the system.
CREATE USER IF NOT EXISTS 'inventory_admin'@'localhost' IDENTIFIED BY 'Admin@12345';
CREATE USER IF NOT EXISTS 'inventory_manager'@'localhost' IDENTIFIED BY 'Manager@12345';

GRANT role_admin TO 'inventory_admin'@'localhost';
GRANT role_inventory_manager TO 'inventory_manager'@'localhost';

SET DEFAULT ROLE role_admin TO 'inventory_admin'@'localhost';
SET DEFAULT ROLE role_inventory_manager TO 'inventory_manager'@'localhost';

FLUSH PRIVILEGES;

-- 3) BACKUP / RECOVERY (run these in shell, not inside MySQL)
-- Backup:
-- mysqldump -u root -p Personal_Finance > inventory_management_backup.sql
--
-- Restore:
-- mysql -u root -p Personal_Finance < inventory_management_backup.sql

-- 4) SECURITY IDEAS FOR REPORT
-- - Principle of least privilege via roles.
-- - Separate admin and inventory operator accounts.
-- - Restrict DELETE for manager role.
-- - Use strong passwords and local-only access for demo environment.
-- - Schedule regular mysqldump backups and test restoration.
