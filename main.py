import logging
import os
import pandas as pd
from pathvalidate import sanitize_filename
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import RecorderScraper.spiders.api_search_spiders as apispiders
import RecorderScraper.spiders.docsearch_spiders as docsearch
import RecorderScraper.spiders.official_records_spiders as officialrecords
import RecorderScraper.spiders.other_spiders as other
import RecorderScraper.spiders.recordworks_spiders as recorderworks
from RecorderScraper.helpers import load_input_keywords_from_excel, load_scraped_data_from_jsonl
from RecorderScraper.spiders.entity_spider import EntitySpider
from export import generate_excel_report, export_manager_and_member_data

logger = logging.getLogger(__name__)


def main():
    # BURROW = GRANTOR
    # LENDER = GRANTEE

    settings = get_project_settings()
    scraping_mode = settings.get('SCRAPING_MODE')
    if scraping_mode not in {'grantees', 'grantor', 'entity'}:
        raise Exception('Unknown scraping mode: {}'.format(scraping_mode))

    scraped_data_file_name = settings.get('DATA_FILE')
    input_excel_file_path = settings.get('INPUT_FILE')
    output_excel_file_path = settings.get('OUTPUT_FILE')

    process = CrawlerProcess(settings, install_root_handler=False)

    # logging
    configure_logging()
    file_handler = logging.FileHandler('scrapy_errors.log')
    file_handler.setLevel(logging.WARNING)
    logging.root.handlers.append(file_handler)
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

    OUTPUT_DIR = os.path.join(desktop_path, 'Recorder\\')
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    PDF_DIRECTORY = os.path.join(OUTPUT_DIR, 'PDF_files\\')
    if not os.path.exists(PDF_DIRECTORY):
        os.makedirs(PDF_DIRECTORY)

    # ENTITY SCRAPER
    if scraping_mode == 'entity':

        df = pd.read_excel(OUTPUT_DIR + 'Borrower Name Schedule.xlsx')
        keywords = df.iloc[:, 3].tolist()
        df['Grantor'] = df['Grantor'].apply(lambda x: sanitize_filename(x.replace('_', ' ')))
        file_matching_dict = dict(zip(df['Grantor'], zip(df['Keyword'], df['County'])))

        process.crawl(EntitySpider, pdf_directory=PDF_DIRECTORY, input_keywords=keywords)
        process.start(install_signal_handlers=True)

        export_manager_and_member_data(PDF_DIRECTORY, OUTPUT_DIR + 'parsed_pdfs.xlsx', file_matching_dict)

    # RECORDER SCRAPER
    else:
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
            other.NevadaSpider,

            # Other spiders
            # TODO: NOT WORKING
            other.SanDiegoSpider,

            # TODO: check Kern often not working
            other.KernSpider,
            other.TulareSpider,
            other.PlacerSpider,
            other.MarinSpider,
            other.MendocinoSpider,
        ]

        # all_spiders = {
        #     other.KernSpider
        # }
        # completed_keywords.clear()

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

        if scraping_mode == 'grantor':
            generate_excel_report(output_excel_file_path=OUTPUT_DIR + 'Borrower Name Schedule.xlsx', filter_deed_of_trust_only=True, filter_individuals=True)
        else:
            generate_excel_report(output_excel_file_path=OUTPUT_DIR + 'Lender Name Schedule.xlsx')


if __name__ == '__main__':
    main()
