import datetime
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
    base_url = 'https://aviation-safety.net/database/'

    custom_settings = {
        'LOG_ENABLED': False,
        'ITEM_PIPELINES': {
            'accidents_extraction.pipelines.AccidentsExtractionPipeline': 300,
        }

    }

    start_urls = [
        'https://aviation-safety.net/database/',
    ]

    rules = [
        Rule(
            LinkExtractor(
                restrict_xpaths='//*[@id="contentcolumn"]/div/p[3]/a',
                restrict_css='a[href*=Year]',
                deny=r'.+lang=[a-z]{2}$',
                # process_value=lambda x: x if x.endswith('2020') or x.endswith('2019') else None
            ),
            callback='parse_accidents_for_year',
            follow=True,
        )
    ]

    def parse_accidents_for_year(self, response):
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
            value = self._correct_str(' '.join(all_text[1:]))
            data[key] = value

        narrative = response.xpath('///*[@id="contentcolumn"]/div/span[2]')
        narrative = ''.join(narrative.css('*::text').extract())
        data['Narrative'] = self._correct_str(narrative)

        cause = response.xpath('//*[@id="contentcolumn"]/div/span[3]').css('*::text').extract()
        data['ProbableCause'] = self._correct_str(''.join(cause))

        data = self._process_accident_data(data)
        if not data:
            return
        else:
            yield data

    def _process_accident_data(self, data: Dict):
        accident = items.Accident()
        if 'Date' not in data:
            return
        accident['status'] = data.get('Status', None)
        accident['time'] = self._parse_time(data.get('Time', None))
        accident['weekday'], accident['day'], accident['month'], accident['year'] = (
            self._parse_date(data['Date'])
        )
        accident['aircraft_type'] = data['Type']
        accident['operator'] = self._parse_operator(data)
        accident['country'], accident['location'] = self._parse_location(data['Location'])
        accident['phase'] = self._parse_phase(data.get('Phase', 'Unknown'))
        accident['nature'] = self._parse_nature(data.get('Nature', 'Unknown'))
        accident['aircraft_damage'] = data.get('Aircraft damage', 'Unknown')
        accident['narrative'] = data.get('Narrative', None)
        accident['probable_cause'] = data.get('ProbableCause', None)
        accident['departure_airport'] = self._parse_airport(
            data.get('Departure airport', 'Unknown')
        )
        accident['destination_airport'] = self._parse_airport(
            data.get('Destination airport', 'Unknown')
        )
        accident['first_flight'] = self._parse_first_flight(data.get('First flight', None))
        accident['engines'] = data.get('Engines', None)
        accident['total_airframe_hrs'] = data.get('Total airframe hrs', None)

        accident.update(self._parse_people_data(data))

        return accident

    @staticmethod
    def _correct_str(x: str) -> str:
        if not x:
            return
        x = x.encode("ascii", errors="ignore").decode()
        x = re.sub(r' +', ' ', x.rstrip()).strip()
        return x

    @staticmethod
    def _parse_time(x: str) -> str:
        if not x:
            return

        # ca or c. means circa which translated from latin means approximate
        x = x.replace('ca', '').replace('c.', '').replace(' ', '')

        if re.match(r'^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$', x):
            return str(datetime.datetime.strptime(x, '%H:%M').time())
        elif re.match(r'^(2[0-3]|[01]?[0-9]):([0-5]?[0-9]):([0-5]?[0-9])$', x):
            return str(datetime.datetime.strptime(x, '%H:%M:%S').time())
        else:
            return

    @staticmethod
    def _parse_date(x: str) -> Tuple:

        def get_month(month_str: str) -> int:
            if 'xx' in month_str.lower():
                return

            if len(month_str) == 3:
                return time.strptime(month_str, "%b").tm_mon
            else:
                return time.strptime(month_str, "%B").tm_mon

        x = x.split()
        if len(x) == 3:
            weekday, day, month, year = None, None, x[-2], x[-1]
            try:
                month, year = get_month(month), int(year)
            except ValueError:
                month, year = None, None
        elif len(x) == 4:
            [weekday, day, month, year] = x
            try:
                day, month, year = int(day), get_month(month), int(year)
            except ValueError:
                day, month, year = None, None, None
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
    def _parse_location(x: str) -> Tuple:
        country = x.rstrip("*")[x.rfind("(") + 1:-1]
        country = country.strip()
        x = x[: -(len(country) + 4)].strip()

        if not country or country == 'Unknown country':
            country = 'Unknown'

        if not x:
            x = 'Unknown'

        return country, x

    @staticmethod
    def _parse_phase(x: str) -> str:
        if not x:
            return 'Unknown'
        elif x in ('()', '(CMB)', 'Unknown (UNK)'):
            return 'Unknown'
        else:
            return x

    @staticmethod
    def _parse_nature(nature: str) -> str:
        if not nature or nature == '-':
            return 'Unknown'
        else:
            return nature

    @staticmethod
    def _parse_airport(x: str) -> str:
        if not x or x in ('?', '-'):
            return 'Unknown'
        else:
            return x

    @staticmethod
    def _parse_people_data(data: Dict) -> Dict:
        output = {}
        for name in ('Crew', 'Passengers', 'Total'):

            try:
                [data_1, data_2] = [x.strip() for x in data[name].split('/')]
                if 'Occupants' in data_1 and 'Fatalities' in data_2:
                    occupants_data, fatalities_data = data_1, data_2
                elif 'Occupants' in data_2 and 'Fatalities' in data_1:
                    occupants_data, fatalities_data = data_2, data_1
                else:
                    occupants_data, fatalities_data = None, None
            except ValueError:
                occupants_data, fatalities_data = None, None

            if not occupants_data and fatalities_data:
                occupants, fatalities = None, None
            else:
                occupants = list(map(int, re.findall(r'\d+', occupants_data)))
                occupants = (occupants[0:1] or (None,))[0]

                fatalities = list(map(int, re.findall(r'\d+', fatalities_data)))
                fatalities = (fatalities[0:1] or (None,))[0]

            if fatalities and not occupants:
                occupants = fatalities

            output[f'{name.lower()}_occupants'] = occupants
            output[f'{name.lower()}_fatalities'] = fatalities
        return output

    @classmethod
    def _parse_first_flight(cls, first_flight: str) -> int:
        first_flight = cls._correct_str(first_flight)
        if not first_flight:
            return
        else:
            try:
                return int(first_flight[:4])
            except ValueError:
                return

    @classmethod
    def _parse_airframe_hrs(cls, hours: str) -> int:
        hours = cls._correct_str(hours)
        if not hours:
            return
        else:
            try:
                return int(hours)
            except ValueError:
                return
