from scrapy import Request

from RecorderScraper.spiders.base_spiders.recorderworks_base_spider import RecorderWorksBaseSpider


class OrangeSpider(RecorderWorksBaseSpider):
    name = 'Orange'

    def __init__(self, *args, **kwargs):
        super().__init__('https://cr.ocgov.com/recorderworks/', *args, **kwargs)


class ContraCostaSpider(RecorderWorksBaseSpider):
    name = 'Contra Costa'

    def __init__(self, *args, **kwargs):
        super().__init__('https://crsecurepayment.com/RW/', *args, **kwargs)


class SanMateoSpider(RecorderWorksBaseSpider):
    name = 'San Mateo'

    def __init__(self, *args, **kwargs):
        super().__init__('https://apps.smcacre.org/recorderworks/', *args, **kwargs)


class StanislausSpider(RecorderWorksBaseSpider):
    name = 'Stanislaus'

    def __init__(self, *args, **kwargs):
        super().__init__('https://crweb.stancounty.com/RecorderWorksInternet/', *args, **kwargs)


class ImperialSpider(RecorderWorksBaseSpider):
    name = 'Imperial'

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorder.co.imperial.ca.us/RecorderWorksInternet/', *args, **kwargs)


class MercedSpider(RecorderWorksBaseSpider):
    name = 'Merced'

    def __init__(self, *args, **kwargs):
        super().__init__('https://web2.co.merced.ca.us/RecorderWorksInternet/', *args, **kwargs)
        self.start_urls = ['https://web2.co.merced.ca.us/RecorderWorksInternet/Account/Login.aspx?ReturnUrl=%2fRecorderWorksInternet%2f']
        raise NotImplementedError()

    def get_search_requests(self, document_type='') -> list[Request]:
        return super().get_search_requests('')[1:]


class SiskiyouSpider(RecorderWorksBaseSpider):
    name = 'Siskiyou'

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorder.co.siskiyou.ca.us/RecorderWorksInternet/', *args, **kwargs)


class AmadorSpider(RecorderWorksBaseSpider):
    name = 'Amador'

    def __init__(self, *args, **kwargs):
        super().__init__('https://mint.amadorgov.org/RecorderWorksInternet/', *args, **kwargs)


class ModocSpider(RecorderWorksBaseSpider):
    name = 'Modoc'

    def __init__(self, *args, **kwargs):
        super().__init__('https://rwindex.co.modoc.ca.us/recorderworksinternet/', *args, **kwargs)
