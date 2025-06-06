CREATE DATABASE IF NOT EXISTS ctf;
USE ctf;

CREATE USER IF NOT EXISTS 'ctfuser'@'%' IDENTIFIED BY 'ctfpass';
GRANT ALL PRIVILEGES ON ctf.* TO 'ctfuser'@'%';
FLUSH PRIVILEGES;


CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    custom_order_id VARCHAR(50) UNIQUE,
    user_id INT,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    delivery_address TEXT,
    country TEXT,
    mobileNum TEXT,
    zipCode INT,
    city TEXT,
    status ENUM('pending', 'shipped', 'delivered') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (username, password) VALUES
('jkal56@gmail.com','Jk246al!');

INSERT INTO orders (custom_order_id, user_id, product_name, quantity, delivery_address, country, mobileNum, zipCode, city, status) VALUES
('2df4-daf6910253ce85db', 1, 'Best Juice Shop Salesman Artwork', 1, 'Meg Alexandrou 5', 'Greece', '6955458867', '54640', 'Thessaloniki', 'pending');