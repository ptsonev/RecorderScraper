from scrapy import Request, FormRequest

from RecorderScraper.spiders.base_spiders.docsearch_base_spider import DocSearchBaseSpider


class RiversideSpider(DocSearchBaseSpider):
    name = 'Riverside'
    # https://webselfservice.riversideacr.com/Web/search/DOCSEARCH2111S1
    docsearch_doc_type = ['DEED OF TRUST/MORTGAGE - ASSIGNMENT', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://webselfservice.riversideacr.com/Web/', 'DOCSEARCH2111S1', *args, **kwargs)


class SanBernardinoSpider(DocSearchBaseSpider):
    name = 'SanBernardino'
    # https://arcselfservice.sbcounty.gov/web/search/DOCSEARCH516S1
    docsearch_doc_type = ['ASSIGNMENT DEED OF TRUST', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://arcselfservice.sbcounty.gov/web/', 'DOCSEARCH516S1', *args, **kwargs)


class FresnoSpider(DocSearchBaseSpider):
    name = 'Fresno'
    # https://fresnocountyca-web.tylerhost.net/web/search/DOCSEARCH377S1
    docsearch_doc_type = ['ASSIGNMENT OF TRUST DEED', 'DEED OF TRUST', 'ASGT-ASGT TD']

    def __init__(self, *args, **kwargs):
        super().__init__('https://fresnocountyca-web.tylerhost.net/web/', 'DOCSEARCH377S1', *args, **kwargs)


class VenturaSpider(DocSearchBaseSpider):
    name = 'Ventura'
    # https://clerkrecorderselfservice.ventura.org/web/search/DOCSEARCH17S1
    docsearch_doc_type = ['ASSIGNMENT DEED OF TRUST', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://clerkrecorderselfservice.ventura.org/web/', 'DOCSEARCH17S1', *args, **kwargs)


class SonomaSpider(DocSearchBaseSpider):
    name = 'Sonoma'
    # https://crarecords.sonomacounty.ca.gov/selfserviceweb/search/DOCSEARCH429S1
    docsearch_doc_type = ['ASGT TRUST DEED', 'TRUST DEED']

    def __init__(self, *args, **kwargs):
        super().__init__('https://crarecords.sonomacounty.ca.gov/Web/', 'DOCSEARCH429S1', *args, **kwargs)
        self.start_urls = ['https://crarecords.sonomacounty.ca.gov/Web/user/disclaimer']


class SantaBarbaraSpider(DocSearchBaseSpider):
    name = 'SantaBarbara'
    # https://records.sbcrecorder.com/web/search/DOCSEARCH439S1
    docsearch_doc_type = ['ASSIGNMENT DEED OF TRUST', 'DEED OF TRUST', 'DEED OF TRUST-ASSIGNMENT']

    def __init__(self, *args, **kwargs):
        super().__init__('https://records.sbcrecorder.com/web/', 'DOCSEARCH439S1', *args, **kwargs)


class MontereySpider(DocSearchBaseSpider):
    name = 'Monterey'
    # https://montereycountyca-web.tylerhost.net/Montereyweb/search/DOCSEARCH284S3
    docsearch_doc_type = ['ASSIGNMENT OF DEED OF TRUST', 'TRUST DEED']

    def __init__(self, *args, **kwargs):
        super().__init__('https://montereycountyca-web.tylerhost.net/Montereyweb/', 'DOCSEARCH284S3', *args, **kwargs)


class ButteSpider(DocSearchBaseSpider):
    name = 'Butte'
    # https://recorder.buttecounty.net/web/search/DOCSEARCH201S5
    docsearch_doc_type = ['ASSIGNMENT OF DEED OF TRUST', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorder.buttecounty.net/web/', 'DOCSEARCH201S5', *args, **kwargs)


class YoloSpider(DocSearchBaseSpider):
    name = 'Yolo'
    # NOTE: It seems there is no ASSIGNMENT OF DEED OF TRUST
    # https://yolocountyca-web.tylerhost.net/web/search/DOCSEARCH201S5
    docsearch_doc_type = ['DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://yolocountyca-web.tylerhost.net/web/', 'DOCSEARCH201S5', *args, **kwargs)


class ElDoradoSpider(DocSearchBaseSpider):
    name = 'ElDorado'
    # https://recorderclerkservice.edcgov.us/elweb/search/DOCSEARCH458S5
    docsearch_doc_type = ['ASSIGNMENT DEED OF TRUST', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorderclerkservice.edcgov.us/elweb/', 'DOCSEARCH458S5', *args, **kwargs)


class ShastaSpider(DocSearchBaseSpider):
    name = 'Shasta'
    # https://recorderselfservice.co.shasta.ca.us/web/search/DOCSEARCH344S4
    docsearch_doc_type = ['ASSIGNMENT OF DEED OF TRUST', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorderselfservice.co.shasta.ca.us/web/', 'DOCSEARCH344S4', *args, **kwargs)


class MaderaSpider(DocSearchBaseSpider):
    name = 'Madera'
    # https://maderacountyca-web.tylerhost.net/web/search/DOCSEARCH201S5
    docsearch_doc_type = ['Asgt/DT', 'Deed of Trust']

    def __init__(self, *args, **kwargs):
        super().__init__('https://maderacountyca-web.tylerhost.net/web/', 'DOCSEARCH201S5', *args, **kwargs)


class YubaSpider(DocSearchBaseSpider):
    name = 'Yuba'
    # https://recorder.co.yuba.ca.us:8443/web/search/DOCSEARCH143S1
    docsearch_doc_type = ['ASSIGNMENT OF DEED OF TRUST', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorder.co.yuba.ca.us:8443/web/', 'DOCSEARCH143S1', *args, **kwargs)


class SanBenitoSpider(DocSearchBaseSpider):
    name = 'SanBenito'
    # https://sanbenitocountyca-web.tylerhost.net/web/search/DOCSEARCH395S2
    docsearch_doc_type = ['DEED OF TRUST/ASSIGNMENT', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://sanbenitocountyca-web.tylerhost.net/web/', 'DOCSEARCH395S2', *args, **kwargs)


class CalaverasSpider(DocSearchBaseSpider):
    name = 'Calaveras'
    # https://recorderweb.calaverasgov.us/web/search/DOCSEARCH215S1
    docsearch_doc_type = ['ASSIGNMENT/DT', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorderweb.calaverasgov.us/web/', 'DOCSEARCH215S1', *args, **kwargs)


class DelNorteSpider(DocSearchBaseSpider):
    name = 'DelNorte'
    # https://delnortecountyca-web.tylerhost.net/web/search/DOCSEARCH201S5
    docsearch_doc_type = ['ASSIGNMENT OF TRUST DEED', 'DEED OF TRUST']

    def __init__(self, *args, **kwargs):
        super().__init__('https://delnortecountyca-web.tylerhost.net/web/', 'DOCSEARCH201S5', *args, **kwargs)


class InyoSpider(DocSearchBaseSpider):
    name = 'Inyo'
    docsearch_doc_type = ['ASSIGNMENT OF DEED OF TRUST', 'TRUST DEED']

    def __init__(self, *args, **kwargs):
        super().__init__('https://inyococa-web.tylerhost.net/web/', 'DOCSEARCH477S1', *args, **kwargs)


class AlpineSpider(DocSearchBaseSpider):
    name = 'Alpine'
    # https://erss.alpinecountyca.gov/web/search/DOCSEARCH4S1
    docsearch_doc_type = ['ASSIGN OF DEED OF TRUST', 'TRUST DEEDS']

    def __init__(self, *args, **kwargs):
        super().__init__('https://erss.alpinecountyca.gov/web/', 'DOCSEARCH4S1', *args, **kwargs)


class SanLuisObispoSpider(DocSearchBaseSpider):
    """
    Cloudflare, may stop working in the future
    """
    name = 'San Luis Obispo'
    # https://crrecords.slocounty.ca.gov/SLOWeb/search/DOCSEARCH262S3
    docsearch_doc_type = ['ASSIGNMENT OF DEED OF TRUST', 'DEED OF TRUST']

    custom_settings = {
        'DOWNLOAD_DELAY': 5
    }

    def __init__(self, *args, **kwargs):
        super().__init__('https://crrecords.slocounty.ca.gov/SLOWeb/', 'DOCSEARCH262S3', *args, **kwargs)


class SanJoaquinSpider(DocSearchBaseSpider):
    """
    Imperva, may stop working in the future
    """
    name = 'San Joaquin'
    # https://sser.sjgov.org/Web/search/DOCSEARCH3032S8
    docsearch_doc_type = ['Deed Of Trust-Assignment', 'Deed Of Trust']

    def __init__(self, *args, **kwargs):
        super().__init__('https://sser.sjgov.org/Web/', 'DOCSEARCH3032S8', *args, **kwargs)

    def get_search_requests(self, document_type: str = '') -> list[Request]:
        start_date, end_date = self.get_date_range()
        search_post_data = {
            'field_BothNamesID': self.current_keyword['keyword'],
            'field_RecDateID_DOT_StartDate': start_date,
            'field_RecDateID_DOT_EndDate': end_date,
        }

        return [
            FormRequest(url=self.search_post_url, headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie, formdata=search_post_data),
            Request(url=self.search_results_url, headers=self.DEFAULT_AJAX_REQUEST_HEADER, cookies=self.docsearch_disclaimer_cookie),
        ]
