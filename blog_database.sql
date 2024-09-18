CREATE DATABASE blog_db;

USE blog_db;

CREATE TABLE blogs (
id int auto_increment PRIMARY KEY,
author VARCHAR(50) NOT NULL,
title VARCHAR(50) NOT NULL,
content TEXT NOT NULL,
tag VARCHAR(50)
);


CREATE TABLE users (
id int auto_increment PRIMARY KEY,
public_id VARCHAR(50) unique,
name VARCHAR(50) NOT NULL,
password VARCHAR(255) NOT NULL,
admin BOOLEAN DEFAULT FALSE
)