from scrapy import Request, FormRequest, Selector
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class MarinSpider(RecorderBaseSpider):
    name = 'Marin'
    NO_RECORDS_FOUND = 'No records were found.'

    def __init__(self, *args, **kwargs):
        self.init_url = 'https://apps.marincounty.org/RecordersIndexSearch?%EE%80%80ShowDisclaimer=False'
        self.search_url = 'https://apps.marincounty.org/RecordersIndexSearch'

        self.start_urls = [self.init_url]
        super().__init__(document_type_list=['ASSIGNMENT OF DEED OF TRUST', 'DEED OF TRUST'], *args, **kwargs)

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        return [
            self.get_search_request_helper(document_type)
        ]

    def get_search_request_helper(self, document_type_id: str, page: int = 0) -> Request:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']
        query_data = {
            'Action': 'N',
            'NLN': keyword,
            'NDT': document_type_id,
            'NSD': start_date,
            'NED': end_date,
            'NFN': '',
            'NMI': '',
            'GCPG': str(page),
        }
        return FormRequest(url=self.search_url, method='GET', cb_kwargs={'document_type_id': document_type_id}, formdata=query_data)

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> list[Request]:
        next_page = self.get_next_page_helper(response, current_page=current_page, total_pages_regex=r'<div>(\d+) pages')

        # zero based paging
        if next_page is not None:
            return self.get_search_request_helper(document_type, current_page - 1)

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        if '?Action=' not in response.url:
            return [(Request(url=response.url), None)]

        details_data = self.parse_item_details_from_search_results(response, url_or_id='//td/a[contains(@href, "DN=")]/@href')
        return self.construct_item_details_requests(details_data)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('recording_date', '//td[normalize-space(text())="Recording Date:"]/following-sibling::td/text()')
        item_loader.add_xpath('document_type', '//td[normalize-space(text())="Document Title:"]/following-sibling::td/text()')

        grantees = self.parse_html_table('Grantees:', item_loader.context['selector'])
        item_loader.add_value('grantees', grantees)

        grantor = self.parse_html_table('Grantors:', item_loader.context['selector'])
        item_loader.add_value('grantor', grantor)

    @staticmethod
    def parse_html_table(field_name: str, selector: Selector):
        result = []
        xpath = f'//tr[td[normalize-space(text())="{field_name}"]]/following-sibling::tr|//tr[td[normalize-space(text())="{field_name}"]]'
        for row in selector.xpath(xpath):
            row_header = (row.xpath('td[1]/text()').get() or '').strip()
            row_value = (row.xpath('td[2]/text()').get() or '').strip()
            if row_header == '' or row_header == field_name:
                result.append(row_value)
            else:
                break
        return result

    def get_disclaimer_requests(self, response) -> list[Request]:
        pass
