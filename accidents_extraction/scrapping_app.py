import argparse
import logging
import os

import accidents_extraction.spiders.accidents as accidents
import accidents_extraction.spiders.aircraft as aircraft
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from utils import read_json

logging.getLogger('scrapy').propagate = False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-type', choices=['accident', 'aircraft'], required=True,
                        help='Defines to scrap "accident" or "aircraft" data.')
    parser.add_argument('--output-type', choices=['mysql_db', 'json'], required=True)
    parser.add_argument('--db-config', help='Config json file for MySQL database.')
    parser.add_argument('--output-json-path',
                        help='The output json path, if the output type is "json".')
    return parser.parse_args()


settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'accidents_extraction.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')

if __name__ == "__main__":
    args = parse_args()
    if args.output_type == 'json':
        if not args.output_json_path:
            raise ValueError('Please provide output json path')

        process = CrawlerProcess(
            settings={
                'FEED_FORMAT': 'json',
                'FEED_URI': args.output_json_path
            },
        )

    else:
        if not args.db_config:
            raise ValueError('Please provide db config file.')

        settings.set('DB_SETTINGS', read_json(args.db_config))
        process = CrawlerProcess(
            settings=settings
        )

    if args.data_type == 'accident':
        process.crawl(accidents.AccidentsSpider)
    else:
        process.crawl(aircraft.AircraftSpider)
    process.start()  # the script will block here until the crawling is finished
