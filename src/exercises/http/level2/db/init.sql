CREATE DATABASE IF NOT EXISTS ctf2;
USE ctf2;


CREATE USER IF NOT EXISTS 'ctfuser2'@'%' IDENTIFIED BY 'ctfpass2';
GRANT ALL PRIVILEGES ON ctf2.* TO 'ctfuser2'@'%';
FLUSH PRIVILEGES;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

INSERT INTO users (username, password) VALUES
('georgekon', 'K0n67jl!'),
('marylunar', 'pa55w0rd!23'),
('alexelef', 'a1ex56@3k');
