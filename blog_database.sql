CREATE DATABASE blog_db;

USE blog_db;

CREATE TABLE blogs (
id int auto_increment PRIMARY KEY,
title VARCHAR(50) NOT NULL,
content TEXT NOT NULL,
tag VARCHAR(50)
)
