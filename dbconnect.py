import MySQLdb

"""
CREATE DATABASE BDBankAndes;
CREATE TABLE users (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    password VARCHAR(100),
                    email VARCHAR(40),
                    created_date DATETIME);

CREATE TABLE comments (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                        user_id INT(11),
                        text VARCHAR(200),
                        created_date DATETIME,
                        FOREIGN KEY(user_id) REFERENCES users(id));
"""

def connection():
    conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='SQLS3rv3r',
    db='BDBankAndes'
    )

    c = conn.cursor()

    return c, conn
