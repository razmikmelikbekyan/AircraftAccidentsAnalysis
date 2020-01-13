import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'crashes_2015'

TABLE = (
    "CREATE TABLE `crashes` ("
    "  `status` varchar(50),"
    "  `date` date NOT NULL,"
    "  `aircraft_type` varchar(100) NOT NULL,"
    "  `operator` varchar(100),"
    "  `location` varchar(100),"
    "  `id` INT(10) NOT NULL AUTO_INCREMENT,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


cnx = mysql.connector.connect(user='root', password='ubuntu2020')

cursor = cnx.cursor()
try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

try:
    print("Creating table:")
    cursor.execute(TABLE)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
        print("already exists.")
    else:
        print(err.msg)
else:
    print("OK")

cursor.close()
cnx.close()
