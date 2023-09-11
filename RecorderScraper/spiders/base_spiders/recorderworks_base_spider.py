from urllib.parse import urljoin

from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class RecorderWorksBaseSpider(RecorderBaseSpider):
    name = 'RecorderWorks Base Spider'
    NO_RECORDS_FOUND = '>0</span>  Result'
    DEFAULT_DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, domain: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.domain = domain

        self.search_post_url = urljoin(self.domain, f'Presentors/SearchHelpPresentor.aspx')
        self.search_results_url = urljoin(self.domain, f'Presentors/AjaxPresentor.aspx')
        self.details_page_url = urljoin(self.domain, f'Presentors/DetailsPresentor.aspx')

        self.details_page_format_url = self.details_page_url + '?resultsCount=0&docid={}'

        self.start_urls = [self.domain]

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        item_details = self.parse_item_details_from_search_results(response,
                                                                   url_or_id='.//input[normalize-space(@id)="EntityTitleDocNum_docId"]/@value',
                                                                   rows_xpath='//tr[normalize-space(@class)="searchResultRow"]',
                                                                   document_type='.//div[normalize-space(@class)="DocTypeContainer"]/p/text()',
                                                                   recording_date='.//td[normalize-space(@id)="recDate"]/text()',
                                                                   url_format=self.details_page_format_url)

        details_post_data = {
            'ImgIsPCOR': 'False',
            'ImgIsDTT': 'False',
            'ImgIsOBIndex': 'False',
            'ImgIsOBIndexCell': 'False',
            'OBBookTab': '',
            'OBBookSeq': '',
            'OBIndexPage': '',
            'OBIndexCell': '',
            'OBDocImageBook': '',
            'OBDocImagePage': '',
            'OBDocImageType': '',
            'OBDocImageRecYear': '',
            'OBDocImageFormType': '',
            'ImgIsRef': 'False',
            'FromBasket': 'False',
            'FitToSize': 'False',
            'ERetrievalGroup': '1',
            'IsNewSearch': 'True',
            'resultsCount': '0',
            'BookFirstPage': '0',
            'docIdIndex': '0',
            'imgIndex': '0',
            'docid': '$url_or_id',
            'ImgIsOBDocImage': 'False'
        }
        item_requests = self.construct_item_details_requests(item_details,
                                                             post_url=self.details_page_url,
                                                             method='POST',
                                                             form_post_data=details_post_data,
                                                             documents_need_filtering=True)
        return item_requests

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        search_post_data = self.get_search_post_data_helper()
        return [
            FormRequest(url=self.search_post_url, formdata=search_post_data),
            FormRequest(url=self.search_results_url, formdata=search_post_data),
        ]

    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> Request:
        if ';">Next</td>' in response.text:
            pagination_post_data = self.get_search_post_data_helper(current_page + 1)
            return FormRequest(url=self.search_results_url, formdata=pagination_post_data)

    def parse_item(self, item_loader: ItemLoader):
        item_loader.add_xpath('grantees', '//div[normalize-space(@id)="Grantees"]//text()')
        item_loader.add_xpath('grantor', '//div[normalize-space(@id)="Grantors"]//text()')

    def get_search_post_data_helper(self, page: int = -1) -> dict[str, str]:
        start_date, end_date = self.get_date_range()
        query_data = {
            'PartyType': '0',
            'NameForSearch': self.current_keyword['keyword'],
            'AllowPartial': 'true',
            'FromDate': start_date,
            'ToDate': end_date,
            'ERetrievalGroup': '1',
            'SearchMode': '1',
        }
        if page == -1:
            query_data['IsNewSearch'] = 'true'
        else:
            query_data['PageNum'] = str(page)

        return query_data

    def get_search_filter_requests(self, response: Response) -> list[Request]:
        pass

    def get_disclaimer_requests(self, response) -> list[Request]:
        pass
