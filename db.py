import pymysql

def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="tusk_portal",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )
