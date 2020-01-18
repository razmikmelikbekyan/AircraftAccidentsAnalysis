# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Accident(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    status = scrapy.Field()
    weekday = scrapy.Field()
    day = scrapy.Field()
    month = scrapy.Field()
    year = scrapy.Field()
    # time = scrapy.Field()
    aircraft_type = scrapy.Field()
    operator = scrapy.Field()
    # first_flight = scrapy.Field()
    # crew_occupants = scrapy.Field()
    # crew_fatalities = scrapy.Field()
    # passengers_occupants = scrapy.Field()
    # passengers_fatalities = scrapy.Field()
    # total_occupants = scrapy.Field()
    # total_fatalities = scrapy.Field()
    # aircraft_damage = scrapy.Field()
    country = scrapy.Field()
    location = scrapy.Field()
