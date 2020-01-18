import argparse
import json
import logging
import os
from typing import Dict

import accidents_extraction.spiders.accidents as accidents
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

logging.getLogger('scrapy').propagate = False


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-type', choices=['mysql_db', 'json'], required=True)
    parser.add_argument('--db-config', help='Config json file for MySQL database.')
    parser.add_argument('--output-json-path',
                        help='The output json path, if the output type is "json".')
    return parser.parse_args()


def read_json(json_path: str) -> Dict:
    """Reads JSON file."""
    with open(json_path, 'r') as infile:
        return json.load(infile)


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

    process.crawl(accidents.AccidentsSpider)
    process.start()  # the script will block here until the crawling is finished
