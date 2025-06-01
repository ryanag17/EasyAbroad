-- 02_native_plugin.sql
-- Force our “user” (the same MYSQL_USER that docker-compose gave us) to use mysql_native_password
-- instead of caching_sha2_password.  That way aiomysql can connect without requiring extra crypto.

ALTER USER 'user'@'%' IDENTIFIED WITH mysql_native_password BY 'userpassword';
