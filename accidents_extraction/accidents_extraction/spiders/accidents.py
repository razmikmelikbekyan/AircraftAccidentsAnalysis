import re
import time
from typing import Dict, Tuple
from urllib.parse import urljoin

import accidents_extraction.items as items
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from logger import logger


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
                # process_value=lambda x: x if x.endswith('2020') or x.endswith('2019') else None
            ),
            callback='parse_year',
            follow=True,
        )
    ]

    def parse_year(self, response):
        # extracting table rows
        urls = response.xpath('//*[@id="contentcolumnfull"]/div')

        # first column (clickable date)
        urls = urls.css('table').xpath('tr/td[1]').css('a::attr(href)').getall()

        year = re.findall('Year=[0-9]{4}', response.url)[0][-4:]
        if not urls:
            logger.warn(f'For year={year} no accidents found.')
        else:
            logger.info(f'For year={year} {len(urls)} accidents have been found.')

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
        if not data or not data['year']:
            return
        else:
            yield data

    def _process_accident_data(self, data: Dict):
        accident = items.Accident()
        if 'Date' not in data:
            return
        accident['status'] = data.get('Status', None)
        accident['time'] = data.get('Time', None)
        accident['weekday'], accident['day'], accident['month'], accident['year'] = (
            self._parse_date(data['Date'])
        )
        accident['aircraft_type'] = data['Type']
        accident['operator'] = self._correct_str(self._parse_operator(data))
        accident['country'], accident['location'] = self._parse_location(data['Location'])
        accident['phase'] = self._correct_str(data.get('Phase', 'Unknown (UNK)'))
        accident['nature'] = self._parse_nature(data.get('Nature', 'Unknown'))
        accident['aircraft_damage'] = self._correct_str(data.get('Aircraft damage', 'Missing'))
        accident['narrative'] = self._correct_str(data.get('Narrative', None))
        accident['probable_cause'] = self._correct_str(data.get('ProbableCause', None))
        accident['departure_airport'] = self._correct_str(data.get('Departure airport', 'Unknown'))
        accident['destination_airport'] = self._correct_str(
            data.get('Destination airport', 'Unknown')
        )
        accident['first_flight'] = self._parse_first_flight(data.get('First flight', None))
        accident['engines'] = self._correct_str(data.get('Engines', None))
        accident['total_airframe_hrs'] = self._correct_str(data.get('Total airframe hrs', None))

        accident.update(self._parse_people_data(data))

        return accident

    @staticmethod
    def _parse_date(date_str: str) -> Tuple:

        def get_month(month_str: str) -> int:
            if 'xx' in month_str.lower():
                return None

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
        location = AccidentsSpider._correct_str(location)
        country = location.rstrip("*")[location.rfind("(") + 1:-1]
        country = country.strip()
        location = location[: -(len(country) + 4)].strip()
        return country, location

    @staticmethod
    def _parse_nature(nature: str) -> str:
        nature = AccidentsSpider._correct_str(nature)
        if not nature or nature == '-':
            return 'Unknown'
        else:
            return nature

    @staticmethod
    def _parse_people_data(data: Dict) -> Dict:
        output = {}
        for name in ('Crew', 'Passengers', 'Total'):
            name_data = list(map(int, re.findall(r'\d+', data[name])))
            occupants = (name_data[0:1] or (None,))[0]
            fatalities = (name_data[1:2] or (None,))[0]

            if fatalities and not occupants:
                occupants = fatalities

            output[f'{name.lower()}_occupants'] = occupants
            output[f'{name.lower()}_fatalities'] = fatalities
        return output

    @staticmethod
    def _parse_first_flight(first_flight: str) -> int:
        first_flight = AccidentsSpider._correct_str(first_flight)
        if not first_flight:
            return None
        else:
            try:
                return int(first_flight[:4])
            except ValueError:
                return None

    @staticmethod
    def _parse_airframe_hrs(hours: str) -> int:
        hours = AccidentsSpider._correct_str(hours)
        if not hours:
            return None
        else:
            try:
                return int(hours)
            except ValueError:
                return None

    @staticmethod
    def _correct_str(x: str) -> str:
        if not x:
            return None
        x = x.encode("ascii", errors="ignore").decode()
        x = re.sub(r' +', ' ', x.rstrip()).strip()
        return x
