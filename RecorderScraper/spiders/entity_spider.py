import json
import os
import shutil
from datetime import datetime

import pandas as pd
import scrapy
from name_matching.name_matcher import NameMatcher
from pathvalidate import sanitize_filename
from scrapy import Request
from scrapy.http import Response
from scrapy.http.request.json_request import JsonRequest

from RecorderScraper.helpers import format_whitespaces, remove_non_az_digits


class EntitySpider(scrapy.Spider):
    name = 'Entity Spider'

    API_HEADERS = {
        'authorization': 'undefined',
        'Origin': 'https://bizfileonline.sos.ca.gov',
        'Accept': '*/*',
    }

    custom_settings = {
        'COOKIES_ENABLED': False,
        'HTTPCACHE_ENABLED': True,

        # 'FILES_STORE': '/PDF_files',
        # 'ITEM_PIPELINES': {
        #     'RecorderScraper.pipelines.PDFPipeline': 1
        # }
    }

    def __init__(self, input_keywords: list[str], pdf_directory: str, **kwargs):
        self.input_keywords = list(input_keywords)
        self.pdf_directory = pdf_directory

        if os.path.exists(self.pdf_directory):
            shutil.rmtree(self.pdf_directory)

        os.makedirs(self.pdf_directory)

        super().__init__(**kwargs)

    def start_requests(self):
        for keyword in self.input_keywords:
            payload = {
                'SEARCH_VALUE': keyword,
                'SEARCH_FILTER_TYPE_ID': '0',
                'SEARCH_TYPE_ID': '1',
                'FILING_TYPE_ID': '',
                'STATUS_ID': '',
                'FILING_DATE': {
                    'start': None,
                    'end': None
                },
                'CORPORATION_BANKRUPTCY_YN': False,
                'CORPORATION_LEGAL_PROCEEDINGS_YN': False,
                'OFFICER_OBJECT': {
                    'FIRST_NAME': '',
                    'MIDDLE_NAME': '',
                    'LAST_NAME': ''
                },
                'NUMBER_OF_FEMALE_DIRECTORS': '99',
                'NUMBER_OF_UNDERREPRESENTED_DIRECTORS': '99',
                'COMPENSATION_FROM': '',
                'COMPENSATION_TO': '',
                'SHARES_YN': False,
                'OPTIONS_YN': False,
                'BANKRUPTCY_YN': False,
                'FRAUD_YN': False,
                'LOANS_YN': False,
                'AUDITOR_NAME': '',
                # 'SORT_BY_ID': 'FILING_DATE',
                # 'SORT_BY_DIRECTION': 'DESC',
            }
            yield JsonRequest(url='https://bizfileonline.sos.ca.gov/api/Records/businesssearch', data=payload, headers=self.API_HEADERS, cb_kwargs={'keyword': keyword})

    def parse(self, response: Response, **kwargs):
        try:
            json_data = json.loads(response.text)

            current_search_results = []
            for row_index, value in json_data['rows'].items():
                title = value['TITLE']
                if len(title) != 1:
                    raise Exception('TITLE length error.')

                entity_id = value['RECORD_NUM'].strip()
                title_formatted = format_whitespaces(title[0].replace(f'({int(entity_id)})', ''))
                filling_date = datetime.strptime(value['FILING_DATE'], '%m/%d/%Y').date()
                current_search_results.append((entity_id, title_formatted, filling_date, remove_non_az_digits(title_formatted)))

            if not current_search_results:
                return

            current_search_results.sort(key=lambda x: x[2], reverse=True)
            title_to_match = remove_non_az_digits(kwargs['keyword'])

            filtered_data = [item for item in current_search_results if item[-1] == title_to_match]

            if not filtered_data and len(current_search_results) == 1:
                filtered_data = current_search_results

            if len(filtered_data) == 0 and current_search_results:
                input_df = pd.DataFrame(current_search_results, columns=['entity_id', 'title', 'filling_date', 'title_formatted'])

                matcher = NameMatcher(number_of_matches=1,
                                      legal_suffixes=True,
                                      common_words=False,
                                      top_n=50,
                                      verbose=False)
                matcher.set_distance_metrics(['bag', 'typo', 'refined_soundex'])
                matcher.load_and_process_master_data(column='title', df_matching_data=input_df, transform=True)

                to_match_df = pd.DataFrame([kwargs['keyword']], columns=['title'])
                matches = matcher.match_names(to_be_matched=to_match_df, column_matching='title')
                combined = pd.merge(input_df, matches, how='left', left_index=True, right_on='match_index')
                combined = pd.merge(combined, to_match_df, how='left', left_index=True, right_index=True)

                top_score = combined['score'][0]
                top_entity_id = combined['entity_id'][0]

                if top_score >= 70:
                    filtered_data.append((top_entity_id,))
                else:
                    return

            matched_result_id = filtered_data[0][0]
            sanitized_keyword = sanitize_filename(kwargs['keyword'].replace('_', ' '))
            file_name = f'{sanitized_keyword}_{matched_result_id}.pdf'

            yield Request(url=f'https://bizfileonline.sos.ca.gov/api/History/business/{matched_result_id}', cb_kwargs={'file_name': file_name}, headers=self.API_HEADERS, callback=self.parse_history)

        except Exception as ex:
            self.logger.exception(ex)

    def parse_history(self, response: Response, **kwargs):
        for item in json.loads(response.text)['AMENDMENT_LIST']:
            amendment_type = item['AMENDMENT_TYPE'].upper().strip()
            if amendment_type == 'STATEMENT OF INFORMATION' and item['DOWNLOAD_LINK']:
                yield response.follow(item['DOWNLOAD_LINK'], callback=self.save_pdf, cb_kwargs=kwargs)
                return


    def save_pdf(self, response: Response, **kwargs):
        file_path = os.path.join(self.pdf_directory,  kwargs['file_name'])
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(response.body)
