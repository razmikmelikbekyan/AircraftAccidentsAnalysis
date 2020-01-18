import logging
import os

import accidents_extraction.spiders.accidents as accidents
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'accidents_extraction.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')

logging.getLogger('scrapy').propagate = False

if __name__ == "__main__":
    process = CrawlerProcess(
        settings=settings,
        # settings={
        #     'FEED_FORMAT': 'json',
        #     'FEED_URI': 'items.json'
        # },
    )

    process.crawl(accidents.AccidentsSpider)
    process.start()  # the script will block here until the crawling is finished
