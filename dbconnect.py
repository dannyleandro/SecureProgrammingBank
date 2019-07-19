import MySQLdb
import os


def connection():
    conn = MySQLdb.connect(
    host=os.environ['HOSTDB'],
    user=os.environ['USERDB'],
    passwd=os.environ['PASSDB'],
    db=os.environ['NAMEDB']
    )

    c = conn.cursor()

    return c, conn
