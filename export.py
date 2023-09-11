import logging
from itertools import groupby
from operator import itemgetter

import openpyxl
from openpyxl.worksheet.table import TableStyleInfo, Table
from openpyxl.worksheet.worksheet import Worksheet
from scrapy.utils.project import get_project_settings

from RecorderScraper.helpers import load_scraped_data_from_jsonl, parse_recording_date

logger = logging.getLogger(__name__)


def auto_fit_columns(worksheet: Worksheet):
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(100, length * 1.33)


def set_table_style(worksheet: Worksheet, table_name: str, table_style: str = 'TableStyleMedium2'):
    table_style = TableStyleInfo(name=table_style,
                                 showFirstColumn=False,
                                 showLastColumn=False,
                                 showRowStripes=True,
                                 showColumnStripes=False)
    worksheet.freeze_panes = 'A2'
    table = Table(displayName=table_name, ref=worksheet.dimensions)
    table.tableStyleInfo = table_style
    worksheet.add_table(table)


def prettify_columns(input_names: list[str]):
    return [n.replace('_', ' ').title() for n in input_names]


def _generate_excel_report(scraped_data: list[dict[str, str]], scraping_mode: str, output_excel_file_path: str = 'output.xlsx'):
    workbook = openpyxl.Workbook()
    workbook.remove(workbook['Sheet'])

    results_sheet_columns = ['keyword', 'county', scraping_mode, 'recording_date', 'document_type', 'document_url']

    # Grantee/Grantor Results Sheet
    results_sheet = workbook.create_sheet('Results')
    results_sheet.append(prettify_columns(results_sheet_columns))

    unique_names = set()
    all_results = []
    for current_record in scraped_data:
        current_names_list = current_record.get(scraping_mode)
        if current_record.get('last_record') or not current_names_list:
            continue

        for name in current_names_list:
            if name in unique_names:
                continue
            unique_names.add(name)

            current_result = dict.fromkeys(results_sheet_columns)
            for key in current_result.keys():
                value = current_record.get(key)
                if key == 'recording_date':
                    current_result[key] = parse_recording_date([value])
                else:
                    current_result[key] = value

            current_result[scraping_mode] = name

            all_results.append(current_result)

    all_results.sort(key=itemgetter('county', scraping_mode))
    for result in all_results:
        results_sheet.append(list(result.values()))

    set_table_style(results_sheet, 'results')
    auto_fit_columns(results_sheet)

    # County Counter Sheet
    results_count_by_county_sheet = workbook.create_sheet(f'{scraping_mode.title()} Count by County')
    results_count_by_county_sheet.append(['County', f'Names Found'])
    for key, group in groupby(all_results, key=itemgetter('county')):
        results_count_by_county_sheet.append([key, len(list(group))])

    set_table_style(results_count_by_county_sheet, 'county')
    auto_fit_columns(results_count_by_county_sheet)

    # Lender Counter Sheet
    documents_found_sheet = workbook.create_sheet('Documents Count by Lender')
    documents_found_sheet.append(['Lender(Keyword)', 'Start Date', 'End Date', 'Documents Found'])
    results = [
        list(key) + [len([i for i in group if not i['last_record']])]
        for key, group in groupby(sorted(scraped_data, key=itemgetter('keyword', 'start_date', 'end_date')),
                                  key=itemgetter('keyword', 'start_date', 'end_date'))
    ]
    results.sort(key=lambda x: x[3], reverse=True)
    for result in results:
        documents_found_sheet.append(result)

    set_table_style(documents_found_sheet, 'lender')
    auto_fit_columns(documents_found_sheet)

    workbook.save(output_excel_file_path)


def generate_excel_report():
    logger.info('Preparing the Excel report. Please wait...')
    settings = get_project_settings()
    scraping_mode = settings.get('SCRAPING_MODE')
    scraped_data_file_name = settings.get('DATA_FILE')
    output_excel_file_path = settings.get('OUTPUT_FILE')
    scraped_data = load_scraped_data_from_jsonl(scraped_data_file_name)
    _generate_excel_report(scraped_data, scraping_mode=scraping_mode, output_excel_file_path=output_excel_file_path)
    logger.info(f'All data was successfully saved to {output_excel_file_path}')


def main():
    generate_excel_report()


if __name__ == '__main__':
    main()
