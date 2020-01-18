import re
import time
from typing import Dict, Tuple
from urllib.parse import urljoin

import accidents_extraction.items as items
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider


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
        if not data['year']:
            return
        else:
            yield data

    def _process_accident_data(self, data: Dict):
        accident = items.Accident()
        accident['status'] = data['Status']
        accident['weekday'], accident['day'], accident['month'], accident['year'] = (
            self._parse_date(data['Date'])
        )
        accident['aircraft_type'] = data['Type']
        accident['operator'] = self._parse_operator(data)
        accident['country'], accident['location'] = self._parse_location(data['Location'])
        return accident

    @staticmethod
    def _parse_date(date_str: str) -> Tuple:

        def get_month(month_str: str) -> int:
            if len(month_str) == 3:
                return time.strptime(month_str, "%b").tm_mon
            else:
                return time.strptime(month_str, "%B").tm_mon

        date_str = date_str.split()
        if len(date_str) == 3:
            weekday, day, month, year = None, None, date_str[-2], date_str[-1]
            month, year = get_month(month), int(year)
        elif len(date_str) == 4:
            [weekday, day, month, year] = date_str
            day, month, year = int(day), get_month(month), int(year)
        else:
            weekday, day, month, year = None, None, None, None
        return weekday, day, month, year

    @staticmethod
    def _parse_operator(data: Dict) -> str:
        operator = data.get('Operator', '')
        if not operator:
            operator = data.get('Operating for', '')
        return operator.encode("ascii", errors="ignore").decode()

    @staticmethod
    def _parse_location(location: str) -> Tuple:
        location = location.encode("ascii", errors="ignore").decode()
        location = location.rstrip()
        location = re.sub(r' +', ' ', location)
        country = location.rstrip("*")[location.rfind("(") + 1:-1]
        country = country.strip()
        location = location[: -(len(country) + 4)].strip()
        return country, location
