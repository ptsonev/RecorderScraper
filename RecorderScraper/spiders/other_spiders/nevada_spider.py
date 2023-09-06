from scrapy import Request, FormRequest
from scrapy.http import Response

from RecorderScraper.spiders.other_spiders.san_diego import SanDiegoSpider


class NevadaSpider(SanDiegoSpider):
    name = 'Nevada'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_url = 'https://recorder.mynevadacounty.com/'
        self.disclaimer_url = 'https://recorder.mynevadacounty.com/AcclaimWeb/search/Disclaimer?st=/AcclaimWeb/search/SearchTypeName'

        self.search_url = 'https://recorder.mynevadacounty.com/AcclaimWeb/search/SearchTypeName?Length=6'
        self.grid_results_url = 'https://recorder.mynevadacounty.com/AcclaimWeb/Search/GridResults'

        self.details_url = 'https://recorder.mynevadacounty.com/AcclaimWeb/details/documentdetails/{}'

        self.start_urls = [self.init_url]

    def get_search_filter_requests(self, response: Response) -> list[Request]:
        return self.get_grid_results_request()

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        keyword = self.current_keyword['keyword']
        search_post_data = {
            'IsParsedName': 'False',
            'Both': 'Both',
            'PartyType': 'Both',
            'SearchOnName': keyword,
            'DateRangeList': '',
            'DocTypes': '114,168,169',
            'DocTypesDisplay-input': 'ASSIGNMENT OF TRUST DEED (033),TRUST DEED (118),TRUST DEED & ASSIGNMENT (119)',
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
