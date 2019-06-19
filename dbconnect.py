import MySQLdb

"""
CREATE DATABASE BDBankAndes;
CREATE TABLE users (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    password VARCHAR(100),
                    email VARCHAR(40),
                    created_date DATETIME);

CREATE TABLE otps (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                    otp INT(9),
                    user_id INT(11),
                    created_date DATETIME,
                    used_date DATETIME,
                    active CHAR (10),
                    FOREIGN KEY(user_id) REFERENCES users(id));

CREATE TABLE accounts (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                        user_id INT(11),
                        amount INT(15),
                        created_date DATETIME,
                        last_use_date DATETIME,
                        active CHAR (10),
                        FOREIGN KEY(user_id) REFERENCES users(id));
ALTER TABLE accounts AUTO_INCREMENT = 1000;

CREATE TABLE transactions (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                            account_id INT(11),
                            account_id_dest INT(11),
                            username_dest VARCHAR(50),
                            amount INT(20),
                            type VARCHAR(30),
                            otp INT(9),
                            created_date DATETIME,
                            FOREIGN KEY(account_id) REFERENCES accounts(id));
"""

def connection():
    conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='admin', #'SQLS3rv3r',
    db='BDBankAndes'
    )

    c = conn.cursor()

    return c, conn
