import logging
import re
from abc import abstractmethod
from datetime import datetime

import scrapy
from scrapy import Request, Selector, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.defer import maybe_deferred_to_future

from RecorderScraper.helpers import remove_non_az
from RecorderScraper.items import RecorderItem


def configure_logging_extended(logging_format: str = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'):
    modules = [
        # 'scrapy.statscollectors',
        'scrapy.crawler',
        'scrapy.utils.log',
        'scrapy.middleware',
        'scrapy.core.engine',
        'scrapy.core.scraper',
        'scrapy.addons',
        __name__
    ]
    for module in modules:
        logger = logging.getLogger(module)
        logger.setLevel(logging.WARNING)

    for handler in logging.root.handlers:
        handler.formatter = NoTracebackFormatter(logging_format)
        handler.addFilter(ContentFilter())


class RecorderBaseSpider(scrapy.Spider):
    name = 'Recorder Base Spider'
    start_urls = []

    NO_RECORDS_FOUND = ''
    DEFAULT_DATE_FORMAT = '%#m/%#d/%Y'
    DEFAULT_AJAX_REQUEST_HEADER = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }

    RESULTS_PER_PAGE = -1

    # this will be used if the search results cannot be filtered by document type
    document_type_filter = {
        'ASGMTTD',
        'ASGTTRD',
        'ASGTTRDEED',
        'ASSIGNMENTDEEDOFTRUST',
        'ASSIGNMENTDEEDTR',
        'ASSIGNMENTOFDEEDOFTRUST',
        'ASSIGNMENTOFTRUSTDEED',
        'ASGTTRUSTDEED',
        'ASSIGNTD',
        'DEEDOFTRUST',
        'TDASGT',
        'TDASSIGN',
        'TRUSTDEED',
        'TRUSTDEEDDEEDOFTRUST',
    }

    def __init__(self, input_keywords: list[dict], document_type_list: list[str] = None, *args, **kwargs):

        self.input_keywords = list(input_keywords)
        self.current_keyword = None
        self.max_pages = 1000

        self.document_type_list = document_type_list or ['']

        configure_logging_extended()

        super().__init__(**kwargs)

    async def parse(self, response: Response, **kwargs):

        MAXIMUM_ERRORS_ALLOWED = 15
        current_errors = 0

        disclaimer_requests = self.get_disclaimer_requests(response)
        if disclaimer_requests:
            await self.execute_requests_inline(disclaimer_requests)

        for self.current_keyword in self.input_keywords:
            try:
                for document_type in self.document_type_list:
                    search_requests = self.get_search_requests(document_type)
                    for page in range(1, self.max_pages):
                        search_response = await self.execute_requests_inline(search_requests)
                        if page == 1 and self.NO_RECORDS_FOUND not in search_response.text:
                            filter_requests = self.get_search_filter_requests(search_response)
                            if filter_requests:
                                search_response = await self.execute_requests_inline(filter_requests)

                        unfiltered_item_requests = self.get_item_details_requests(search_response)
                        if not unfiltered_item_requests and self.NO_RECORDS_FOUND not in search_response.text:
                            raise Exception(f'Search error for {self.current_keyword} Possible reason - too many records were found.')
                            # self.logger.error(f'Search error for {self.current_keyword}\nPossible reason - too many records were found.')

                        filtered_item_requests = []
                        if unfiltered_item_requests:
                            for item_request, document_types in unfiltered_item_requests:

                                if document_types is None:
                                    filtered_item_requests.append(item_request)
                                else:
                                    formatted_document_types = [remove_non_az(doc) for doc in document_types]
                                    if any(doc_type in formatted_document_types for doc_type in self.document_type_filter):
                                        filtered_item_requests.append(item_request)

                        for index, item_request in enumerate(filtered_item_requests):
                            if 'grantees' not in item_request.cb_kwargs:
                                item_response = await self.execute_requests_inline(item_request)
                                current_item = self._parse_item(item_response)
                            else:
                                current_item = self._parse_item(item_request)

                            test_fields = ['grantor', 'grantees']
                            for test_field in test_fields:
                                if not current_item.get(test_field):
                                    self.logger.error(f'No {test_field} found for {current_item["document_url"]}')

                            yield current_item

                        # get pagination requests
                        search_requests = self.get_next_search_page_request(search_response, document_type=document_type, current_page=page)

                        # check if we reach the last page
                        if search_requests is None or page == self.max_pages - 1:
                            # add a dummy last record here
                            dummy_item = RecorderItem(self.current_keyword)
                            dummy_item['last_record'] = True
                            dummy_item['county'] = self.name
                            yield dummy_item
                            break

            except Exception as ex:
                current_errors = current_errors + 1
                if current_errors >= MAXIMUM_ERRORS_ALLOWED:
                    self.logger.error(f'The scraping will stop for {self.name} County. Reason: too many errors occurred. Start URL: {self.start_urls[0]}')
                    return
                # self.logger.exception(ex)

    def _parse_item(self, response: Response):
        item_loader = ItemLoader(item=RecorderItem(), response=response)
        item_loader.add_value('keyword', self.current_keyword['keyword'])
        item_loader.add_value('start_date', self.current_keyword['start_date'])
        item_loader.add_value('end_date', self.current_keyword['end_date'])
        item_loader.add_value('county', self.name)
        item_loader.add_value('document_url', response.url)

        recorder_fields = RecorderItem.fields.keys()
        for key, value in response.cb_kwargs.items():
            if key in recorder_fields:
                item_loader.replace_value(key, value)

        self.parse_item(item_loader)
        current_item = item_loader.load_item()

        return current_item

    @abstractmethod
    def parse_item(self, item_loader: ItemLoader):
        pass

    @abstractmethod
    def get_disclaimer_requests(self, response: Response) -> list[Request]:
        pass

    @abstractmethod
    def get_search_requests(self, document_type: str = '') -> list[Request]:
        raise NotImplementedError(self.name)

    @abstractmethod
    def get_search_filter_requests(self, response: Response) -> list[Request]:
        pass

    @abstractmethod
    def get_next_search_page_request(self, response: Response, document_type: str = '', current_page: int = -1) -> Request:
        pass

    @abstractmethod
    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        pass

    @classmethod
    def parse_item_details_from_search_results(cls, response: Response, url_or_id: str = None, url_format: str = None, rows_xpath: str = None, document_type: str = None, recording_date: str = None, **kwargs):

        all_results = []
        if rows_xpath:
            for current_result in cls.execute_xpath_or_jmespath(response, rows_xpath):
                url_or_id_value = (cls.execute_xpath_or_jmespath(current_result, url_or_id).get() or '').strip()

                input_dict = dict(document_type=document_type, recording_date=recording_date, **kwargs)
                result_data = {
                    'response': response,
                    'selector': current_result,
                    'url_or_id': url_or_id_value,
                }
                for key, xpath in input_dict.items():
                    if not xpath:
                        continue
                    result_data[key] = cls.execute_xpath_or_jmespath(current_result, xpath).getall()

                all_results.append(result_data)
        else:
            for current_result in cls.execute_xpath_or_jmespath(response, url_or_id):
                result_data = {
                    'response': response,
                    'url_or_id': current_result.get()
                }
                all_results.append(result_data)

        for result in all_results:
            if url_format:
                result['document_url'] = url_format.format(result['url_or_id'])
            else:
                result['document_url'] = response.urljoin(result['url_or_id'])

        return all_results

    @staticmethod
    def execute_xpath_or_jmespath(response_or_selector, xpath_or_jmespath: str) -> Selector:
        if xpath_or_jmespath[0] == '$':
            return response_or_selector.jmespath(xpath_or_jmespath[1:])
        else:
            return response_or_selector.xpath(xpath_or_jmespath)

    @staticmethod
    def construct_item_details_requests(input_list: list, form_post_data=None, post_url: str = None, method: str = 'GET', headers=None, cookies=None, documents_need_filtering: bool = False):
        all_requests = []
        if input_list:
            for current_meta_data in input_list:
                response: Response = current_meta_data['response']
                if post_url:
                    url = post_url
                else:
                    url = current_meta_data['document_url']

                if form_post_data:
                    _form_post_data = dict()
                    for key, value in form_post_data.items():
                        if value and value[0] == '$' and value[1:] in current_meta_data:
                            _form_post_data[key] = str(current_meta_data[value[1:]])
                        else:
                            _form_post_data[key] = str(value)
                    current_request = FormRequest(url=url, cb_kwargs=current_meta_data, formdata=_form_post_data, method=method, headers=headers, cookies=cookies)

                else:
                    current_request = response.follow(url=url, cb_kwargs=current_meta_data, method=method, headers=headers, cookies=cookies)

                if documents_need_filtering:
                    all_requests.append((current_request, current_meta_data['document_type']))
                else:
                    all_requests.append((current_request, None))

        return all_requests

    @classmethod
    def get_next_page_helper(cls, response: Response, next_page_xpath: str = None, total_pages_regex: str = None, total_results_offset_xpath: str = None, current_page: int = 1):
        if next_page_xpath:
            next_page_url = response.xpath(next_page_xpath).get()
            if next_page_url:
                return response.follow(url=next_page_url)

        if total_pages_regex:
            total_pages_result = re.search(total_pages_regex, response.text)
            if total_pages_result:
                total_pages = int(total_pages_result.group(1))
                if current_page < total_pages:
                    return current_page + 1

        if total_results_offset_xpath:
            if cls.RESULTS_PER_PAGE == -1:
                raise NotImplementedError()

            total_results_result = cls.execute_xpath_or_jmespath(response, total_results_offset_xpath).get()
            if total_results_result:
                total_results = int(total_results_result)
                next_offset = current_page * cls.RESULTS_PER_PAGE
                if next_offset < total_results:
                    return next_offset

        return None

    async def execute_requests_inline(self, input_requests: list[Request]):
        last_response: Response = None
        _input_requests = []
        if isinstance(input_requests, Request):
            _input_requests.append(input_requests)
        else:
            _input_requests.extend(input_requests)

        for input_request in _input_requests:
            last_response = await self.defer_request(input_request)
            if not (200 <= last_response.status < 300):
                raise HttpError(last_response, f'Ignoring response {last_response}: HTTP status code is not handled or not allowed')

            if input_request.callback:
                additional_requests = input_request.callback(last_response)
                if additional_requests:
                    _input_requests.append(additional_requests)

        return last_response

    async def defer_request(self, dfd_request: Request):
        dfd_request = self.crawler.engine.download(dfd_request)
        return await maybe_deferred_to_future(dfd_request)

    def get_date_range(self) -> tuple[str, str]:
        if not self.current_keyword:
            return '', ''
        start_date = self.current_keyword['start_date'].strftime(self.DEFAULT_DATE_FORMAT) if self.current_keyword['start_date'] else ''
        end_date = self.current_keyword['end_date'].strftime(self.DEFAULT_DATE_FORMAT) if self.current_keyword['end_date'] else ''
        return start_date, end_date


class ContentFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'spider'):
            record.name = record.spider.name
        elif hasattr(record, 'crawler'):
            record.name = record.crawler.spidercls.name
        else:
            pass
        return True


class NoTracebackFormatter(logging.Formatter):
    def formatException(self, ei):
        # return ''
        pass

    def formatStack(self, stack_info):
        # return ''
        pass
