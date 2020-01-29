import mysql.connector
from mysql.connector import errorcode


def create_db(conx, cursor, database):
    """For given connection creates database."""
    try:
        cursor.execute("USE {}".format(database))
        print("Successfully using {} database.".format(database))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(database))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            try:
                cursor.execute(
                    "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(database)
                )
            except mysql.connector.Error as err:
                print("Failed creating database: {}".format(err))
                exit(1)
            print("Database {} created successfully.".format(database))
            conx.database = database
        else:
            print(err)
            exit(1)


def create_table(cursor, table_name, table_data):
    """For given cursor creates table."""
    try:
        print(f"Creating table: '{table_name}'.")
        cursor.execute(table_data)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print(f"Table '{table_name}' already exists.")
        else:
            print(err.msg)
    else:
        print(f"Table '{table_name}' successfully created.")
