-- Initialize MySQL database with proper character set and collation
CREATE DATABASE IF NOT EXISTS newapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE newapp_db;

-- Grant privileges to the news app user
GRANT ALL PRIVILEGES ON newapp_db.* TO 'newsapp_user'@'%';
FLUSH PRIVILEGES;


