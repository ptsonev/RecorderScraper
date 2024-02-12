from urllib.request import Request

from scrapy import FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.official_records_base_spider import OfficialRecordsBaseSpider


class TehamaSpider(OfficialRecordsBaseSpider):
    name = 'Tehama'

    def __init__(self, *args, **kwargs):
        super().__init__('http://tehamapublic.countyrecords.com/scripts/hfweb.asp?formuser=public&Application=TEH', *args, **kwargs)


class TrinitySpider(OfficialRecordsBaseSpider):
    name = 'Trinity'

    def __init__(self, *args, **kwargs):
        super().__init__('https://trinityca.countyrecords.com/scripts/hfweb.asp?formuser=public&formpassword=trinityca&Application=TCR', document_type_list=['TD', 'TD14', 'TDA', 'TDA14'], *args, **kwargs)

    def get_search_requests(self, document_type: str = '') -> list[list[Request]]:
        start_date, end_date = self.get_date_range()
        post_data = {
            'APPLICATION': 'TCR',
            'DATABASE': 'OR',
            'BASKET': '',
            'databasename': 'Official Records',
            'SEARCHTYPE7': 'exact',
            'FIELD7': '',
            'FIELD8': document_type,
            'SEARCHTYPE8': 'EXACT',
            'FIELD9': '',
            'FIELD9B': '',
            'FIELD10': start_date,
            'FIELD10B': end_date,
            'SEARCHTYPE11': 'begin',
            'FIELD11': '',
            'SEARCHTYPE12': 'begin',
            'FIELD12': '',
            'CROSSNAMETYPE': 'contains',
            'CROSSNAMEFIELD': self.current_keyword['keyword'],
            'FIELD13': '',
            'SEARCHTYPE17': 'exact',
            'FIELD17': '',
            'DataAction': 'Search'
        }
        return [
            FormRequest(url=self.search_url, formdata=post_data)
        ]

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        item_details = self.parse_item_details_from_search_results(response, url_or_id='//a[contains(@href, "&DocNo=")]/@href')
        return self.construct_item_details_requests(item_details, documents_need_filtering=False)

    def parse_item(self, item_loader: ItemLoader):
        super(TrinitySpider, self).parse_item(item_loader)
        item_loader.add_xpath('recording_date', '//td[normalize-space(text())="File_Date"]/following-sibling::td//text()')
        item_loader.add_xpath('document_type', '//td[normalize-space(text())="Instrument_Type"]/following-sibling::td//text()')
