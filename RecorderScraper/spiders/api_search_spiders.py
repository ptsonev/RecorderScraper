from RecorderScraper.spiders.base_spiders.recorder_api_search_spider import RecorderApiSearchSpider


class SacramentoSpider(RecorderApiSearchSpider):
    name = 'Sacramento'

    def __init__(self, *args, **kwargs):
        super().__init__('https://recordersdocumentindex.saccounty.net/SearchServiceAPI/', document_type_list=['227', '230'], *args, **kwargs)


class SanFranciscoSpider(RecorderApiSearchSpider):
    name = 'San Francisco'

    def __init__(self, *args, **kwargs):
        super().__init__('https://recorder.sfgov.org/SearchService/', document_type_list=['002', '004'], *args, **kwargs)
