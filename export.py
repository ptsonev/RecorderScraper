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


def _generate_excel_report(scraped_data: list[dict[str, str]], output_excel_file_path: str = 'output.xlsx'):
    workbook = openpyxl.Workbook()
    workbook.remove(workbook['Sheet'])

    # Grantee Results Sheet
    grantee_results_sheet = workbook.create_sheet('Results')
    grantee_results_sheet_columns = ['Keyword', 'County', 'Grantee', 'Recording Date', 'Document Type', 'Document Url']
    grantee_results_sheet.append(grantee_results_sheet_columns)

    unique_names = set()
    all_grantee_results = []
    for current_record in scraped_data:
        if current_record.get('last_record') or not current_record.get('grantees'):
            continue

        for grantee in current_record['grantees']:
            if grantee in unique_names:
                continue
            unique_names.add(grantee)

            current_result = dict.fromkeys(grantee_results_sheet_columns)
            for key in current_result.keys():
                output_key = key.replace(' ', '_').lower()
                if key == 'Recording Date':
                    current_result[key] = parse_recording_date([current_record.get(output_key)])
                else:
                    current_result[key] = current_record.get(output_key)

            current_result['Grantee'] = grantee

            all_grantee_results.append(current_result)

    all_grantee_results.sort(key=itemgetter('County', 'Grantee'))
    for grantee in all_grantee_results:
        grantee_results_sheet.append(list(grantee.values()))

    set_table_style(grantee_results_sheet, 'results')
    auto_fit_columns(grantee_results_sheet)

    # County Counter Sheet
    grantees_count_by_county_sheet = workbook.create_sheet('Grantees Count by County')
    grantees_count_by_county_columns = ['County', 'Grantees Found']
    grantees_count_by_county_sheet.append(grantees_count_by_county_columns)

    county_grouping = groupby(all_grantee_results, key=itemgetter('County'))

    for key, group in county_grouping:
        grantees_count_by_county_sheet.append([key, len(list(group))])

    set_table_style(grantees_count_by_county_sheet, 'county')
    auto_fit_columns(grantees_count_by_county_sheet)

    # Lender Counter Sheet
    documents_found_sheet = workbook.create_sheet('Documents Count by Lender')
    documents_found_sheet_columns = ['Lender(Keyword)', 'Start Date', 'End Date', 'Documents Found']
    documents_found_sheet.append(documents_found_sheet_columns)
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
    scraped_data_file_name = next(iter(settings.get('FEEDS', {}).keys()))
    output_excel_file_path = settings.get('OUTPUT_FILE')
    scraped_data = load_scraped_data_from_jsonl(scraped_data_file_name)
    _generate_excel_report(scraped_data, output_excel_file_path=output_excel_file_path)
    logger.info(f'All data was successfully saved to {output_excel_file_path}')


def main():
    generate_excel_report()


if __name__ == '__main__':
    main()
