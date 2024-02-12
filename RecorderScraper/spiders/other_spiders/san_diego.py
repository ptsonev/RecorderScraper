from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class SanDiegoSpider(RecorderBaseSpider):
    name = 'San Diego'
    NO_RECORDS_FOUND = 'No names found. Please try your search again.'

    RESULTS_PER_PAGE = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_url = 'https://arcc-acclaim.sdcounty.ca.gov/'
        self.disclaimer_url = 'https://arcc-acclaim.sdcounty.ca.gov/search/Disclaimer?st=/search/SearchTypeName'
        self.search_url = 'https://arcc-acclaim.sdcounty.ca.gov/search/SearchTypeName?Length=6'
        self.filter_search_results_url = 'https://arcc-acclaim.sdcounty.ca.gov/Search/SearchTypePreName'
        self.grid_results_url = 'https://arcc-acclaim.sdcounty.ca.gov/Search/GridResults'

        self.details_url = 'https://arcc-acclaim.sdcounty.ca.gov/details/documentdetails/{}'

        self.start_urls = [self.init_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']
        search_post_data = {
            'IsParsedName': 'False',
            'Both': 'Both',
            'PartyType': 'Both',
            'SearchOnName': keyword,
            'DateRangeList': '',
            'DocTypes': '518,519',
            'DocTypesDisplay-input': 'ASSIGNMENT OF DEED OF TRUST (006),DEED OF TRUST (007)',
            'DocTypesDisplay': '',
            'RecordDateFrom': start_date,
            'BookTypesDisplay': 'All',
            'BookTypes': 'All',
            'RecordDateTo': end_date,
            'X-Requested-With': 'XMLHttpRequest'
        }
        return [
            FormRequest(url=self.search_url, formdata=search_post_data)
        ]

    def get_search_filter_requests(self, response: Response) -> list[Request]:
        name_list = response.xpath('//li[contains(@class, "t-first")]//input[normalize-space(@name)="itemValue"]/@value').getall()
        start_date, end_date = self.get_date_range()
        filter_post_data = {
            'NameList': '|||'.join(name_list),
            'PartyType': 'Both',
            'RecordDateFrom': start_date,
            'RecordDateTo': end_date,
            'BookTypes': 'All',
            'DocTypes': '518,519',
            'X-Requested-With': 'XMLHttpRequest'
        }

        return [
            FormRequest(url=self.filter_search_results_url, formdata=filter_post_data),
            self.get_grid_results_request()
        ]

    def get_grid_results_request(self, page: int = 1):
        paginate_post_data = {
            'page': str(page),
            'size': str(self.RESULTS_PER_PAGE),
        }
        return FormRequest(self.grid_results_url, formdata=paginate_post_data, method='POST', headers=self.DEFAULT_AJAX_REQUEST_HEADER)

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> list[Request]:
        next_offset = self.get_next_page_helper(response, total_results_offset_xpath='$total', current_page=current_page)
        if next_offset:
            return self.get_grid_results_request(current_page + 1)

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        details_data = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='$TransactionItemId',
                                                                   url_format=self.details_url,
                                                                   rows_xpath='$data[*]',
                                                                   document_type='$DocTypeDescription')

        return self.construct_item_details_requests(details_data)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('recording_date', '//div[normalize-space(@class)="detailLabel" and normalize-space(text())="Record Date:"]/following-sibling::div/text()')
        item_loader.add_xpath('grantees', '//div[normalize-space(@class)="detailLabel" and normalize-space(text())="Grantee:"]/following-sibling::div//text()')
        item_loader.add_xpath('grantor', '//div[normalize-space(@class)="detailLabel" and normalize-space(text())="Grantor:"]/following-sibling::div//text()')

    def get_disclaimer_requests(self, response) -> list[Request]:
        return FormRequest(url=self.disclaimer_url, formdata={'disclaimer': 'true'})
