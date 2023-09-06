from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy.loader import ItemLoader

from RecorderScraper.spiders.base_spiders.recorder_base_spider import RecorderBaseSpider


class PlacerSpider(RecorderBaseSpider):
    name = 'Placer'
    NO_RECORDS_FOUND = 'No documents were found that match the specified criteria.'
    DEFAULT_DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_url = 'https://countyfusion4.kofiletech.us/countyweb/loginDisplay.action?countyname=Placer'
        self.login_url = 'https://countyfusion4.kofiletech.us/countyweb/login.action'
        self.disclaimer_url = 'https://countyfusion4.kofiletech.us/countyweb/disclaimer.do'

        self.search_url = 'https://countyfusion4.kofiletech.us/countyweb/search/searchExecute.do?assessor=false'
        self.search_url_results = 'https://countyfusion4.kofiletech.us/countyweb/search/Placer/docs_SearchResultList.jsp?scrollPos=0&searchSessionId=searchJobMain'

        self.details_url_format = 'https://countyfusion4.kofiletech.us/countyweb/search/displayDocument.do?searchSessionId=searchJobMain&instId={}'

        self.start_urls = [self.init_url]

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']

        search_post_data = {
            'searchCategory': 'ADVANCED',
            'searchSessionId': 'searchJobMain',
            'PLATS': '',
            'QUARTER': '',
            'SEARCHTYPE': 'allNames',
            'RECSPERPAGE': '1000',
            'userRefCode': '',
            'INSTTYPEALL': 'false',
            'INSTTYPE': 'T4,T2',
            'CASETYPE': '',
            'ORDERBY_LIST': '',
            'DATERANGE': '[{"name":"TODATE","value":"User Defined"}]',
            'PARTY': 'both',
            'ALLNAMES': keyword,
            'FROMDATE': start_date,
            'TODATE': end_date,
            'daterange_TODATE': 'User Defined'
        }
        return [
            FormRequest(url=self.search_url, formdata=search_post_data, callback=self.display_search_results)
        ]

    def display_search_results(self, response: Response):
        if response.text.strip() and self.NO_RECORDS_FOUND not in response.text:
            return Request(url=self.search_url_results)

    def get_item_details_requests(self, response: Response) -> list[tuple[Request, list[str]]]:
        details_data = self.parse_item_details_from_search_results(response,
                                                                   rows_xpath='//table[normalize-space(@class)="easyui-datagrid"]/tbody/tr',
                                                                   url_format=self.details_url_format,
                                                                   url_or_id='.//input[normalize-space(@name)="navCB"]/@value',
                                                                   document_type='td[8]/text()',
                                                                   recording_date='td[9]/text()',
                                                                   grantees='td[5]/span/@title|td[5]/span/text()')

        return self.construct_item_details_requests(details_data)

    def parse_item(self, item_loader: ItemLoader):

        all_grantees = set()
        for grantee_list in item_loader.get_output_value('grantees') or []:
            for grantee in grantee_list.split('::'):
                all_grantees.add(grantee)
        item_loader.replace_value('grantees', all_grantees)

    def get_disclaimer_requests(self, response) -> list[Request]:
        token = response.xpath('//input[normalize-space(@name)="token"]/@value').get()
        login_post_data = {
            'cmd': 'login',
            'countyname': 'Placer',
            'scriptsupport': 'yes',
            'apptype': '',
            'datasource': '',
            'userdatasource': '',
            'fraudsleuth': 'false',
            'guest': 'true',
            'public': 'false',
            'startPage': '',
            'CountyFusionForceNewSession': 'true',
            'struts.token.name': 'token',
            'token': token,
            'username': '',
            'password': '',
        }

        return [
            FormRequest(url=self.login_url, formdata=login_post_data),
            FormRequest(url=self.disclaimer_url, formdata={'cmd': 'Accept'})
        ]
