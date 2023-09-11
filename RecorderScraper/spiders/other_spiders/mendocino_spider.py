from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class MendocinoSpider(RecorderBaseSpider):
    name = 'Mendocino'
    NO_RECORDS_FOUND = '>No results found<'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_url = 'http://icris.co.mendocino.ca.us/recorder/web/login.jsp'
        self.disclaimer_url = 'http://icris.co.mendocino.ca.us/recorder/web/loginPOST.jsp'
        self.search_url = 'http://icris.co.mendocino.ca.us/recorder/eagleweb/docSearchPOST.jsp'
        self.start_urls = [self.init_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']
        search_post_data = {
            '__search_select': 'DT',
            '__search_select': 'ADT',
            'BothNamesIDSearchType': 'Basic Searching',
            'GrantorIDSearchType': 'Basic Searching',
            'Return1IDSearchType': 'Basic Searching',
            'NotesIDSearchType': 'Basic Searching',
            'GranteeIDSearchType': 'Basic Searching',
            'BothNamesIDSearchString': keyword,
            'docTypeTotal': '140',
            'RecDateIDEnd': end_date,
            'RecDateIDStart': start_date,
            'GrantorIDSearchString': '',
            'GranteeIDSearchString': '',
            'Return1IDSearchString': '',
            'BookPageIDBook': '',
            'DateOfEventIDStart': '',
            'DateOfEventIDEnd': '',
            'ParcelID': '',
            'BookPageIDPage': '',
            'NotesIDSearchString': '',
            'DocNumID': ''
        }
        return [
            FormRequest(url=self.search_url, formdata=search_post_data)
        ]

    def get_next_search_page_request(self, response: Response, document_type='', current_page: int = -1) -> list[Request]:
        return self.get_next_page_helper(response, next_page_xpath='//a[normalize-space(text())="Next"]/@href')

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        details_data = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='td[1]//a/@href',
                                                                   rows_xpath='//table[normalize-space(@id)="searchResultsTable"]/tbody/tr',
                                                                   document_type='td[1]//a/text()[1]')

        return self.construct_item_details_requests(details_data)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('recording_date', '//span[normalize-space(text())="Recording Date"]/following-sibling::span//text()')
        item_loader.add_xpath('grantees', '//table[normalize-space(@class)="sortableDataTable" and.//th[normalize-space(text())="Grantee"]]//tr/td//text()')
        item_loader.add_xpath('grantor', '//table[normalize-space(@class)="sortableDataTable" and.//th[normalize-space(text())="Grantor"]]//tr/td//text()')

    def get_disclaimer_requests(self, response) -> list[Request]:
        post_data = {
            'guest': 'true',
            'submit': 'Public Login'
        }
        return FormRequest(url=self.disclaimer_url, formdata=post_data)
