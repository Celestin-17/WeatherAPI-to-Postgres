create_database = """CREATE DATABASE IF NOT EXISTS weatherDB;"""

create_table = """CREATE TABLE IF NOT EXISTS weatherTable(
id SERIAL PRIMARY KEY,
date VARCHAR(30) UNIQUE,
weatherid INT,
main VARCHAR(30),
windspeed INT,
humidity INT,
temp INT
);"""

