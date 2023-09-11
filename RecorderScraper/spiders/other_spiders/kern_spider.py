from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class KernSpider(RecorderBaseSpider):
    name = 'Kern'
    NO_RECORDS_FOUND = 'NO MATCHING DOCUMENTS FOUND.'
    DEFAULT_DATE_FORMAT = '%Y%m%d'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_url = 'http://recorderonline.co.kern.ca.us/cgi-bin/osearchg.mbr/input'
        self.search_url = 'http://recorderonline.co.kern.ca.us/cgi-bin/oresultg03.mbr/datedetail?'
        self.user_key = ''

        self.start_urls = [self.init_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']
        search_post_data = {
            'Search_Date_From': start_date,
            'Parm_Date_From': start_date,
            'Search_Date_To': end_date,
            'USERKEY': self.user_key,
            'R1': 'B',
            'RTYPE': 'B',
            'Grantor_Date_Name': keyword,
            'Current_Name': keyword,
            'ButtonName': 'http://recorderonline.co.kern.ca.us:80/cgi-bin/oresultg03.mbr/datedetail?',
            'B2': 'Search By Date'
        }

        return [
            FormRequest(url=self.search_url, formdata=search_post_data)
        ]

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> list[Request]:
        return self.get_next_page_helper(response, next_page_xpath='//a[normalize-space(text())="NEXT 10"]/@href')

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        details_data = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='.//a/@href',
                                                                   rows_xpath='//tr[normalize-space(@valign)="top"]',
                                                                   document_type='td[4]//text()',
                                                                   recording_date='td[2]//text()')

        requests = self.construct_item_details_requests(details_data, documents_need_filtering=True)
        return requests

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('grantor', '//table[th/b[normalize-space(text())="Grantee Names"]]/tr/td[1]//text()')
        item_loader.add_xpath('grantees', '//table[th/b[normalize-space(text())="Grantee Names"]]/tr/td[2]//text()')

    def get_disclaimer_requests(self, response) -> list[Request]:
        return Request(url=self.init_url, callback=self.parse_user_key),

    def parse_user_key(self, response: Response):
        self.user_key = response.xpath('//input[normalize-space(@name)="USERKEY"]/@value').get()
