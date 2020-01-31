# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector

from .mysql_utils import create_db, create_table


class AccidentsExtractionPipeline(object):
    # Add database connection parameters in the constructor
    def __init__(self, database, user, password):
        self.conx = mysql.connector.connect(user=user, password=password, use_unicode=True)
        self.cursor = self.conx.cursor()

        self.database = database
        self.user = user
        self.password = password

        self.table_name = 'accidents'

        # Implement from_crawler method and get database connection info from settings.py

    def create_table(self):
        table_data = (
            f"CREATE TABLE `{self.table_name}` ("
            "  `status` varchar(50),"
            "  `time` TIME,"
            "  `weekday` varchar(20),"
            "  `day` TINYINT,"
            "  `month` TINYINT,"
            "  `year` SMALLINT,"
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
            "  `ground_fatalities` SMALLINT,"
            "  `id` INT(10) NOT NULL AUTO_INCREMENT,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB"
        )
        create_table(self.cursor, self.table_name, table_data)

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            return
        return cls(**db_settings)

    # Connect to the database when the spider starts
    def open_spider(self, spider):
        create_db(self.conx, self.cursor, self.database)
        self.create_table()

    # Insert data records into the database (one item at a time)
    def process_item(self, item, spider):
        keys, values = zip(*item.items())
        keys, values = list(keys), list(values)

        keys.append("id")
        values.append(None)

        dummy_values = ", ".join(['%s'] * len(keys))
        keys = ", ".join(keys)

        sql_command = f"INSERT INTO {self.table_name} ({keys}) VALUES ({dummy_values})"
        self.cursor.execute(sql_command, values)
        self.conx.commit()
        return item

    # When all done close the database connection
    def close_spider(self, spider):
        self.conx.close()


class AircraftExtractionPipeline(object):
    # Add database connection parameters in the constructor
    def __init__(self, database, user, password):
        self.conx = mysql.connector.connect(user=user, password=password, use_unicode=True)
        self.cursor = self.conx.cursor()

        self.database = database
        self.user = user
        self.password = password

        self.table_name = 'aircraft'

        # Implement from_crawler method and get database connection info from settings.py

    def create_table(self):
        table_data = (
            f"CREATE TABLE `{self.table_name}` ("
            "  `aircraft_main_model` varchar(200) NOT NULL,"
            "  `manufacturer` varchar(200),"
            "  `series` varchar(1500),"
            "  `country` varchar(500),"
            "  `icao_type_designator` varchar(500),"
            "  `first_flight` SMALLINT,"
            "  `production_ended` varchar(200),"
            "  `production_total` varchar(200),"
            "  `propulsion` varchar(500),"
            "  `maximum_number_of_passengers` SMALLINT,"
            "  `maximum_take_off_mass` INT,"
            "  `mass_unit` varchar(200),"
            "  `icao_mass_group` SMALLINT,"
            "  PRIMARY KEY (`aircraft_main_model`)"
            ") ENGINE=InnoDB"
        )
        create_table(self.cursor, self.table_name, table_data)

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            return
        return cls(**db_settings)

    # Connect to the database when the spider starts
    def open_spider(self, spider):
        create_db(self.conx, self.cursor, self.database)
        self.create_table()

    # Insert data records into the database (one item at a time)
    def process_item(self, item, spider):
        keys, values = zip(*item.items())
        keys, values = list(keys), list(values)

        dummy_values = ", ".join(['%s'] * len(keys))
        keys = ", ".join(keys)

        sql_command = f"INSERT INTO {self.table_name} ({keys}) VALUES ({dummy_values})"
        self.cursor.execute(sql_command, values)
        self.conx.commit()
        return item

    # When all done close the database connection
    def close_spider(self, spider):
        self.conx.close()
