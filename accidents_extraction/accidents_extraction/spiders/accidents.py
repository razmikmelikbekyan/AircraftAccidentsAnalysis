import logging
from typing import Dict
from urllib.parse import urljoin

import scrapy
from accidents_extraction.items import Accident
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

logging.getLogger('scrapy').propagate = False


class AccidentsSpider(CrawlSpider):
    name = 'accidents'
    start_urls = [
        'https://aviation-safety.net/database/',
    ]
    custom_settings = {'LOG_ENABLED': False}
    base_url = 'https://aviation-safety.net/database/'

    rules = [
        Rule(
            LinkExtractor(
                restrict_xpaths='//*[@id="contentcolumn"]/div/p[3]/a',
                restrict_css='a[href*=Year]',
                deny=r'.+lang=[a-z]{2}$',
                restrict_text='2015'

            ),
            callback='parse_year',
            follow=True,
        )
    ]

    def parse_year(self, response):
        # extracting table rows
        urls = response.xpath('//*[@id="contentcolumnfull"]/div/table//tr')  # all rows
        urls = urls.xpath('td[1]').css('a::attr(href)').getall()  # first column (clickable date)
        for url in urls:
            url = urljoin(self.base_url, url)

            request = scrapy.Request(
                urljoin(self.base_url, url),
                callback=self.parse_accident
            )
            yield request

    def parse_accident(self, response):
        data = {}

        table_rows = response.xpath('//*[@id="contentcolumn"]/div/table//tr')
        for row in table_rows:
            all_text = row.css('*::text').getall()
            key = all_text[0][:-1]
            value = ' '.join(all_text[1:])
            data[key] = value

        narrative = response.xpath('///*[@id="contentcolumn"]/div/span[2]')
        narrative = ''.join(narrative.css('*::text').extract())
        data['Narrative'] = narrative

        cause = response.xpath('//*[@id="contentcolumn"]/div/span[3]').css('*::text').extract()
        data['ProbableCause'] = ''.join(cause)

        data = self._process_accident_data(data)
        if not data['date']:
            return
        else:
            yield data

    def _process_accident_data(self, data: Dict):
        accident = Accident()
        accident['status'] = data['Status']
        accident['date'] = self._parse_date(data['Date'])
        accident['aircraft_type'] = data['Type']
        accident['operator'] = self._get_operator(data)
        accident['location'] = data['Location']
        return accident

    @staticmethod
    def _get_operator(data: Dict) -> str:
        operator = data.get('Operator', '')
        if not operator:
            operator = data.get('Operating for', '')
        return operator

    @staticmethod
    def _parse_date(x: str) -> str:
        mapping = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
        }
        x = x.split()
        if len(x) != 4:
            return
        day = x[1] if len(x[1]) == 2 else f'0{x[1]}'
        month = str(mapping[x[2]]) if mapping[x[2]] >= 10 else f'0{mapping[x[2]]}'
        year = x[3]
        return f'{year}-{month}-{day}'


if __name__ == "__main__":
    process = CrawlerProcess(
        settings={
            'FEED_FORMAT': 'json',
            'FEED_URI': 'items.json'
        }
    )

    process.crawl(AccidentsSpider)
    process.start()  # the script will block here until the crawling is finished
