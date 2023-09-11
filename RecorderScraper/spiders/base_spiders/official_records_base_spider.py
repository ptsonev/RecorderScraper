from urllib.parse import urlparse, urljoin, parse_qs

from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class OfficialRecordsBaseSpider(RecorderBaseSpider):
    name = 'OfficialRecords Base Spider'
    NO_RECORDS_FOUND = '>No hits found. Try a different search.'
    DEFAULT_DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, start_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parsed_url = urlparse(start_url)
        query_parsed = parse_qs(parsed_url.query)

        self.domain = f'{parsed_url.scheme}://{parsed_url.hostname}/'
        self.search_url = urljoin(self.domain, 'scripts/hflook.asp')
        self.application_qs = query_parsed['Application'][0]

        self.start_urls = [start_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        post_data = {
            'APPLICATION': self.application_qs,
            'DATABASE': 'OR',
            'ORDERBY': 'primetable.Recording_Date, primetable.PRSERV',
            'FIELD9': start_date,
            'FIELD9B': end_date,
            'CROSSNAMETYPE': 'contains',
            'CROSSNAMEFIELD': self.current_keyword['keyword'],
            'DataAction': 'Search'
        }
        return [
            FormRequest(url=self.search_url, formdata=post_data)
        ]

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        item_details = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='.//a[b[normalize-space(text())="VIEW"]]/@href',
                                                                   rows_xpath='//tr[td/a/b[normalize-space(text())="VIEW"]]',
                                                                   document_type='td[4]/text()',
                                                                   recording_date='td[5]/text()')

        return self.construct_item_details_requests(input_list=item_details, documents_need_filtering=True)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('grantees', '//td[normalize-space(text())="Grantee"]/following-sibling::td//text()')
        item_loader.add_xpath('grantor', '//td[normalize-space(text())="Grantor"]/following-sibling::td//text()')

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> Request:
        # The website returns all results in a single page
        pass

    def get_disclaimer_requests(self, response) -> list[Request]:
        pass

    def get_search_filter_requests(self, response: Response) -> list[Request]:
        pass
