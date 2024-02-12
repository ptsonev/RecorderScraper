from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class TulareSpider(RecorderBaseSpider):
    name = 'Tulare'
    NO_RECORDS_FOUND = 'returned no matches.'

    def __init__(self, *args, **kwargs):
        super().__init__(document_type_list=['ASSIGNMENT OF DEED OF TRUST', 'DEED OF TRUST'], *args, **kwargs)

        self.init_url = 'https://riimsweb.co.tulare.ca.us/riimsweb/Asp/ORInquiry.asp'
        self.search_url = 'https://riimsweb.co.tulare.ca.us/riimsweb/Asp/ORDocNameList.asp'
        self.start_urls = [self.init_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']
        query_data = {
            'txtPage': '',
            'txtBook': '',
            'txtBegDateControl': start_date,
            'txtEndDateControl': end_date,
            'txtNameControl': keyword,
            'txtDocumentTypeControl': document_type,
            'txtSortBy': 'name',
            'cmdSubmit': 'Submit'
        }
        return FormRequest(url=self.search_url, method='POST', formdata=query_data)

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> list[Request]:
        return self.get_next_page_helper(response, next_page_xpath='//font[normalize-space(@color)="red"]/following-sibling::a/@href')

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        details_data = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='.//a[contains(@href, "ORDocDetail")]/@href',
                                                                   rows_xpath='//tr[normalize-space(@bgcolor)="white" or normalize-space(@bgcolor)="#d6ebf7"]',
                                                                   document_type='td[5]//text()',
                                                                   recording_date='td[6]//text()')

        return self.construct_item_details_requests(details_data)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('grantees', '//table[.//th/p[normalize-space(text())="Grantees:"]]/tr/td[2]//text()')
        item_loader.add_xpath('grantor', '//table[.//th/p[normalize-space(text())="Grantors:"]]/tr/td[1]//text()')

    def get_disclaimer_requests(self, response) -> list[Request]:
        pass
