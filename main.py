import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import RecorderScraper.spiders.api_search_spiders as apispiders
import RecorderScraper.spiders.docsearch_spiders as docsearch
import RecorderScraper.spiders.official_records_spiders as officialrecords
import RecorderScraper.spiders.other_spiders as other
import RecorderScraper.spiders.recordworks_spiders as recorderworks
from RecorderScraper.helpers import load_input_keywords_from_excel, load_scraped_data_from_jsonl
from export import generate_excel_report

logger = logging.getLogger(__name__)


def main():
    # generate_input('data_backup\\Borrower Name Schedule.xlsx')

    settings = get_project_settings()
    scraping_mode = settings.get('SCRAPING_MODE')
    if scraping_mode not in {'grantees', 'grantor'}:
        raise Exception('Unknown scraping mode: {}'.format(scraping_mode))

    scraped_data_file_name = settings.get('DATA_FILE')
    input_excel_file_path = settings.get('INPUT_FILE')

    process = CrawlerProcess(settings, install_root_handler=False)

    # logging
    configure_logging()
    file_handler = logging.FileHandler('scrapy_errors.log')
    file_handler.setLevel(logging.WARNING)
    logging.root.handlers.append(file_handler)

    scraped_data = load_scraped_data_from_jsonl(scraped_data_file_name)
    input_keywords = load_input_keywords_from_excel(input_excel_file_path)
    input_columns = input_keywords[0].keys()
    completed_keywords = [line for line in scraped_data if line.get('last_record')]

    all_spiders = [
        # RecorderWorks spiders
        recorderworks.OrangeSpider,
        recorderworks.ContraCostaSpider,
        recorderworks.SanMateoSpider,
        recorderworks.StanislausSpider,
        recorderworks.MercedSpider,
        recorderworks.ImperialSpider,
        recorderworks.SiskiyouSpider,
        recorderworks.ModocSpider,

        # DOCSEARCH spiders
        docsearch.RiversideSpider,
        docsearch.SanBernardinoSpider,
        docsearch.FresnoSpider,
        docsearch.VenturaSpider,
        docsearch.SanJoaquinSpider,
        docsearch.SonomaSpider,
        docsearch.SantaBarbaraSpider,
        docsearch.MontereySpider,
        docsearch.SanLuisObispoSpider,
        docsearch.ButteSpider,
        docsearch.YoloSpider,
        docsearch.ElDoradoSpider,
        docsearch.ShastaSpider,
        docsearch.MaderaSpider,
        docsearch.YubaSpider,
        docsearch.SanBenitoSpider,
        docsearch.CalaverasSpider,
        docsearch.DelNorteSpider,
        docsearch.InyoSpider,
        docsearch.AlpineSpider,

        # API spiders
        apispiders.SacramentoSpider,
        apispiders.SanFranciscoSpider,

        # Official Records spiders
        officialrecords.TehamaSpider,
        officialrecords.TrinitySpider,

        # San Diego and Nevada are in the same website group, but I implemented them as separate spiders
        # TODO -> merge them into the same base class
        other.SanDiegoSpider,
        other.NevadaSpider,

        # Other spiders
        other.KernSpider,
        other.TulareSpider,
        other.PlacerSpider,
        other.MarinSpider,
        other.MendocinoSpider,
    ]

    # for spider in all_spiders:
    #     print(f'{spider.name}')

    for spider in all_spiders:
        current_completed_keywords = [
            {key: value for key, value in completed.items() if key in input_columns}
            for completed in completed_keywords if completed['county'] == spider.name
        ]

        current_keywords_for_county = [kw for kw in input_keywords if kw not in current_completed_keywords]
        if current_keywords_for_county:
            process.crawl(spider, input_keywords=current_keywords_for_county)
        else:
            logger.info(f'All keywords are already scraped for {spider.name}')

    process.start(install_signal_handlers=True)

    logger.info('Scraping Completed!')

    generate_excel_report()


if __name__ == '__main__':
    main()
