# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector
from mysql.connector import errorcode


class AccidentsExtractionPipeline(object):
    # Add database connection parameters in the constructor
    def __init__(self, database, user, password):
        self.conx = mysql.connector.connect(user=user, password=password, use_unicode=True)
        self.cursor = self.conx.cursor()

        self.database = database
        self.user = user
        self.password = password

        # Implement from_crawler method and get database connection info from settings.py

    def create_db(self):
        try:
            self.cursor.execute("USE {}".format(self.database))
            print("Successfully using {} database.".format(self.database))
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(self.database))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                try:
                    self.cursor.execute(
                        "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.database)
                    )
                except mysql.connector.Error as err:
                    print("Failed creating database: {}".format(err))
                    exit(1)
                print("Database {} created successfully.".format(self.database))
                self.conx.database = self.database
            else:
                print(err)
                exit(1)

    def create_table(self):
        table_data = (
            "CREATE TABLE `accidents` ("
            "  `status` varchar(50),"
            "  `time` varchar(50),"
            "  `weekday` varchar(20),"
            "  `day` TINYINT,"
            "  `month` TINYINT,"
            "  `year` SMALLINT NOT NULL,"
            "  `first_flight` SMALLINT,"
            "  `total_airframe_hrs` INT,"
            "  `aircraft_type` varchar(100) NOT NULL,"
            "  `operator` varchar(100),"
            "  `country` varchar(1000),"
            "  `location` varchar(1000),"
            "  `phase` varchar(1000),"
            "  `nature` varchar(1000),"
            "  `engines` varchar(1000),"
            "  `narrative` TEXT,"
            "  `probable_cause` TEXT,"
            "  `aircraft_damage` varchar(1000),"
            "  `departure_airport` varchar(1000),"
            "  `destination_airport` varchar(1000),"
            "  `crew_occupants` SMALLINT,"
            "  `crew_fatalities` SMALLINT,"
            "  `passengers_occupants` SMALLINT,"
            "  `passengers_fatalities` SMALLINT,"
            "  `total_occupants` SMALLINT,"
            "  `total_fatalities` SMALLINT,"
            "  `id` INT(10) NOT NULL AUTO_INCREMENT,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB"
        )
        try:
            print("Creating table: 'accidents'.")
            self.cursor.execute(table_data)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table 'accidents' already exists.")
            else:
                print(err.msg)
        else:
            print("Table 'accidents' successfully created.")

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise Exception('Not configured')
        return cls(**db_settings)

    # Connect to the database when the spider starts
    def open_spider(self, spider):
        self.create_db()
        self.create_table()

    # Insert data records into the database (one item at a time)
    def process_item(self, item, spider):
        keys, values = zip(*item.items())
        keys, values = list(keys), list(values)

        keys.append("id")
        values.append(None)

        dummy_values = ", ".join(['%s'] * len(keys))
        keys = ", ".join(keys)

        sql_command = f"INSERT INTO accidents ({keys}) VALUES ({dummy_values})"
        self.cursor.execute(sql_command, values)
        self.conx.commit()
        return item

    # When all done close the database connection
    def close_spider(self, spider):
        self.conx.close()
