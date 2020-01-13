# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector


class AccidentsExtractionPipeline(object):
    # Add database connection parameters in the constructor
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password

        self.conx = None
        self.cursor = None

        # Implement from_crawler method and get database connection info from settings.py

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise Exception('Not configured')
        return cls(**db_settings)

    # Connect to the database when the spider starts
    def open_spider(self, spider):
        self.conx = mysql.connector.connect(db=self.database,
                                            user=self.user, password=self.password,
                                            charset='utf8', use_unicode=True)
        self.cursor = self.conx.cursor()

    # Insert data records into the database (one item at a time)
    def process_item(self, item, spider):
        keys = ", ".join(list(item.keys()) + ["id"])
        values = [f"'{x}'" for x in item.values()]
        values = ", ".join(values + ["NULL"])

        sql_command = f"INSERT INTO crashes ({keys}) VALUES ({values})"
        self.cursor.execute(sql_command)
        self.conx.commit()
        return item

    # When all done close the database connection
    def close_spider(self, spider):
        self.conx.close()
