from urllib.parse import urljoin

from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class RecorderApiSearchSpider(RecorderBaseSpider):
    name = 'ApiSearch Base Spider'

    RESULTS_PER_PAGE = 100
    NO_RECORDS_FOUND = '"ResultCount":0,'

    def __init__(self, domain: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.domain = domain

        self.init_url = urljoin(self.domain, 'api/SearchConfiguration')
        self.get_secure_key_url = urljoin(self.domain, 'api/SearchConfiguration/GetSecureKey')
        self.search_url = urljoin(self.domain, 'api/Search/GetSearchResults')
        self.details_url_format = urljoin(self.domain, 'api/search/GetNamesForPagination/{}/1/1000')

        self.start_urls = [self.init_url]

        self.auth_header = {
            'Accept': 'application/json, text/plain, */*',
            'EncryptedKey': '',
            'Password': '',
            'Referer': self.domain,
        }

    def get_search_request_helper(self, document_type: str, page_start: str = '0') -> Request:
        start_date, end_date = self.get_date_range()
        query_data = {
            'ProfileID': 'Public',
            'DocumentClass': 'OfficialRecords',
            'LastName': self.current_keyword['keyword'],
            'SearchText': self.current_keyword['keyword'],
            'IsBasicSearch': 'false',
            'FilingCode': document_type,
            'Rows': str(self.RESULTS_PER_PAGE),
            'MaxRecordedDate': end_date,
            'MinRecordedDate': start_date,
            'NameTypeID': '0',
            'StartRow': page_start,
        }
        return FormRequest(url=self.search_url, formdata=query_data, method='GET', headers=self.auth_header)

    def get_search_requests(self, document_type: str = '') -> list[list[Request]]:
        return [
            self.get_search_request_helper(document_type)
        ]

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> list[Request]:
        next_offset = self.get_next_page_helper(response, current_page=current_page, total_results_offset_xpath='$ResultCount')
        if next_offset:
            return self.get_search_request_helper(document_type, str(next_offset))

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        item_details = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='$ID',
                                                                   url_format=self.details_url_format,
                                                                   rows_xpath='$SearchResults',
                                                                   document_type='$FilingCode',
                                                                   recording_date='$DocumentDate')
        return self.construct_item_details_requests(item_details, headers=self.auth_header)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_jmes('grantees', 'NamesForPagination[?NameTypeDesc==`Grantee`].Fullname')
        item_loader.add_jmes('grantor', 'NamesForPagination[?NameTypeDesc==`Grantor`].Fullname')

        document_type = item_loader.get_output_value('document_type').split('<br/>')
        item_loader.replace_value('document_type', document_type)

    def get_disclaimer_requests(self, response) -> list[Request]:
        return Request(url=self.init_url, headers=self.auth_header, callback=self.parse_auth_token)

    def parse_auth_token(self, response: Response):
        encrypted_key = response.jmespath('HandShakeSecurity.EncryptedKey').get()
        password = response.jmespath('HandShakeSecurity.Password').get()
        self.auth_header['EncryptedKey'] = encrypted_key
        self.auth_header['Password'] = password

    def get_search_filter_requests(self, response: Response) -> list[Request]:
        pass
