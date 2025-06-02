ALTER USER 'user'@'%' IDENTIFIED BY 'userpassword';
GRANT ALL PRIVILEGES ON easyabroad.* TO 'user'@'%';
FLUSH PRIVILEGES;
