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
    first_flight = scrapy.Field()
    time = scrapy.Field()
    aircraft_type = scrapy.Field()
    operator = scrapy.Field()
    crew_occupants = scrapy.Field()
    crew_fatalities = scrapy.Field()
    passengers_occupants = scrapy.Field()
    passengers_fatalities = scrapy.Field()
    total_occupants = scrapy.Field()
    total_fatalities = scrapy.Field()
    ground_fatalities = scrapy.Field()
    phase = scrapy.Field()
    nature = scrapy.Field()
    aircraft_damage = scrapy.Field()
    country = scrapy.Field()
    location = scrapy.Field()
    narrative = scrapy.Field()
    probable_cause = scrapy.Field()
    departure_airport = scrapy.Field()
    destination_airport = scrapy.Field()
    engines = scrapy.Field()
    total_airframe_hrs = scrapy.Field()


class Aircraft(scrapy.Item):
    aircraft_main_model = scrapy.Field()
    manufacturer = scrapy.Field()
    country = scrapy.Field()
    icao_type_designator = scrapy.Field()
    series = scrapy.Field()
    first_flight = scrapy.Field()
    production_ended = scrapy.Field()
    production_total = scrapy.Field()
    propulsion = scrapy.Field()
    maximum_number_of_passengers = scrapy.Field()
    maximum_take_off_mass = scrapy.Field()
    mass_unit = scrapy.Field()
    icao_mass_group = scrapy.Field()
