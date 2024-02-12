from urllib.parse import urljoin, urlencode

from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class DocSearchBaseSpider(RecorderBaseSpider):
    name = 'DOCSEARCH Base Spider'

    docsearch_disclaimer_cookie = {'disclaimerAccepted': 'true'}
    docsearch_doc_type = []
    NO_RECORDS_FOUND = 'No results found, please try a new search or remove applied Filters'

    def __init__(self, domain: str, docsearch: str, *args, **kwargs):

        """
        :param input_keywords:
        :param domain: must include the /web/, /Web/, /elweb/, etc. path
        :param docsearch:
        """

        super().__init__(*args, **kwargs)

        self.domain = domain
        self.docsearch = docsearch
        if not self.docsearch.startswith('DOCSEARCH'):
            self.docsearch = f'DOCSEARCH{self.docsearch}'

        self.init_url = urljoin(self.domain, f'search/{self.docsearch}')
        self.search_post_url = urljoin(self.domain, f'searchPost/{self.docsearch}')
        self.search_results_url = urljoin(self.domain, f'searchResults/{self.docsearch}')
        self.filter_search_results_url = urljoin(self.domain, f'filterSearchResults/{self.docsearch}')

        self.start_urls = [self.init_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:

        start_date, end_date = self.get_date_range()
        search_post_data = {
            'field_BothNamesID': self.current_keyword['keyword'],
            'field_RecordingDateID_DOT_StartDate': start_date,
            'field_RecordingDateID_DOT_EndDate': end_date,
        }

        return [
            FormRequest(url=self.search_post_url, headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie, formdata=search_post_data),
            Request(url=self.search_results_url, headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie),
        ]

    def get_search_filter_requests(self, response: Response) -> list[Request]:
        filter_args = {
            'searchDimension': '|'.join(['DocTypeDesc'] * len(self.docsearch_doc_type)),
            'paths': '|'.join(self.docsearch_doc_type)
        }
        filter_url = urljoin(self.filter_search_results_url, '?' + urlencode(filter_args))

        return [
            Request(url=filter_url, headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie, method='POST'),
            Request(url=self.search_results_url, headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie),
        ]

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> list[Request]:
        next_page = self.get_next_page_helper(response, current_page=current_page, total_pages_regex=r"var totalPages = parseInt\('(\d+)'\)")
        if next_page is not None:
            return Request(url=self.search_results_url + f'?page={next_page}', headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie)

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        item_details = self.parse_item_details_from_search_results(response, url_or_id='//a[normalize-space(@title)="View Document"]/@href')
        return self.construct_item_details_requests(item_details, cookies=self.docsearch_disclaimer_cookie)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('recording_date', '//div[strong[normalize-space(text())="Recording Date:"]]/following-sibling::div/text()')
        item_loader.add_xpath('document_type', '//li[normalize-space(text())="Document Type"]/following-sibling::li/text()')
        item_loader.add_xpath('grantees', '//div[strong[normalize-space(text())="Grantee:"]]/following-sibling::div//li/text()|//div[strong[normalize-space(text())="Grantee:"]]/following-sibling::div/text()')
        item_loader.add_xpath('grantor', '//div[strong[normalize-space(text())="Grantor:"]]/following-sibling::div//li/text()|//div[strong[normalize-space(text())="Grantor:"]]/following-sibling::div/text()')

    def get_disclaimer_requests(self, response) -> list[Request]:
        pass
