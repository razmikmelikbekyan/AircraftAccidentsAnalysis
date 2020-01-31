import re
from typing import Dict, Tuple, List

import accidents_extraction.items as items
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from logger import logger


class AircraftSpider(CrawlSpider):
    name = 'aircraft'
    custom_settings = {
        'LOG_ENABLED': False,
        'ITEM_PIPELINES': {
            'accidents_extraction.pipelines.AircraftExtractionPipeline': 300,
        }

    }

    start_urls = [
        'https://aviation-safety.net/database/type/index.php',
    ]

    rules = [
        Rule(
            LinkExtractor(restrict_xpaths='//*[@id="myTable"]/tbody/tr/td[1]'),
            callback='parse_aircraft',
            follow=True,
        )
    ]

    def parse_aircraft(self, response):
        # extracting aircraft specifications rows
        aircraft_url = response.url
        if not aircraft_url.endswith('/index'):
            logger.warn(f'Aircraft url={aircraft_url} has wrong format.')
            return

        aircraft_url = f'{aircraft_url[:-5]}{"specs"}'
        request = scrapy.Request(aircraft_url, callback=self.parse_aircraft_specs)
        yield request

    def parse_aircraft_specs(self, response):
        data = {}
        try:
            [aircraft_type] = response.xpath('//*[@id="inside"]/div[4]').css('*::text').getall()
        except ValueError:
            return

        aircraft_type = self._correct_str(aircraft_type)
        if not aircraft_type:
            return

        data['aircraft_main_model'] = aircraft_type.replace(' specs', '')

        table_rows = response.xpath('//*[@id="contentcolumnfull"]/div/table//tr')
        for row in table_rows:
            all_text = row.css('*::text').getall()
            key = '_'.join(all_text[0][:-1].replace(':', '').replace('-', '_').split()).lower()
            if key not in items.Aircraft.fields:
                continue
            if key == 'series':
                value = [self._correct_str(x) for x in all_text[1:]]
            else:
                value = self._correct_str(' '.join(all_text[1:]))
            data[key] = value

        yield self._process_aircraft_data(data)

    @staticmethod
    def _correct_str(x: str) -> str:
        if not x:
            return None
        x = x.encode("ascii", errors="ignore").decode()
        x = re.sub(r' +', ' ', x.rstrip()).strip()
        return x

    def _process_aircraft_data(self, data: Dict):
        aircraft = items.Aircraft()
        aircraft['aircraft_main_model'] = data['aircraft_main_model']
        aircraft['manufacturer'] = data.get('manufacturer')
        aircraft['country'] = data.get('country')
        aircraft['icao_type_designator'] = data.get('icao_type_designator')
        aircraft['series'] = self._parse_series(aircraft['manufacturer'], data.get('series'))
        aircraft['first_flight'] = self._parse_first_flight(data.get('first_flight'))
        aircraft['production_ended'] = self._parse_production_ended(data.get('production_ended'))
        aircraft['production_total'] = self._parse_production_total(data.get('production_total'))
        aircraft['propulsion'] = data.get('propulsion')
        aircraft['maximum_number_of_passengers'] = data.get('maximum_number_of_passengers')
        aircraft['maximum_take_off_mass'], aircraft['mass_unit'] = self._parse_mass_data(
            data.get('maximum_take_off_mass', None)
        )
        aircraft['icao_mass_group'] = self._parse_mass_group(data.get('icao_mass_group'))

        return aircraft

    @staticmethod
    def _parse_first_flight(first_flight: str) -> int:
        if not first_flight:
            return None
        else:
            try:
                return int(first_flight[-4:])
            except ValueError:
                return None

    @staticmethod
    def _parse_production_ended(production_ended: str) -> int or str:
        if not production_ended:
            return None
        else:
            if 'ca ' in production_ended:
                production_ended = production_ended.replace('ca ', '')

            if production_ended.isdigit():
                return int(production_ended)
            elif production_ended.isalpha():
                return production_ended
            else:
                return 'UNKNOWN'

    @staticmethod
    def _parse_production_total(production_total: str) -> int or str:
        if not production_total:
            return None
        else:
            if 'ca ' in production_total:
                production_total = production_total.replace('ca ', '')

            if production_total.isdigit():
                return int(production_total)
            else:
                return production_total

    @classmethod
    def _parse_series(cls, manufacturer, series_data: List[str]) -> str:
        if not series_data:
            return

        if len(series_data) == 1:
            series_data = [f'{manufacturer} {x}' for x in series_data[0].split(',')]
        else:
            # series_data = [x for x in series_data if ':' in x]
            series_data = [f'{manufacturer} {x.split(":")[0]}' for x in series_data if ':' in x]
        return '$$'.join([cls._correct_str(x) for x in series_data])

    @staticmethod
    def _parse_mass_data(mass_data: str) -> Tuple:
        if not mass_data:
            return None, None
        else:
            mass, unit = mass_data.split()
            if not mass.isdigit():
                return None, None

            return int(mass), unit

    @staticmethod
    def _parse_mass_group(mass_group: str) -> int:
        if not mass_group:
            return None
        else:
            return int(mass_group)
