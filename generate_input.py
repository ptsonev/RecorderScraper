from datetime import datetime

import pandas as pd

from RecorderScraper.helpers import format_whitespaces


def generate_input(input_file: str, start_year: int = 2020, end_year: int = 2023):
    max_date = datetime.now()

    input_df = pd.read_excel(input_file)
    input_keywords = [format_whitespaces(k).upper() for k in input_df.iloc[:, 0].values[1:]]

    lines = []
    for keyword in input_keywords:
        for year in range(start_year, end_year + 1):
            start_date = datetime(year, 1, 1)
            end_date = min(datetime(year + 1, 1, 1), max_date)
            line = {
                'keyword': keyword,
                'start_date': start_date.strftime('%m/%d/%Y'),
                'end_date': end_date.strftime('%m/%d/%Y')
            }
            lines.append(line)
    file_name = f'keywords_split_{start_year}_{end_year}.xlsx'
    df = pd.DataFrame(lines)
    df.to_excel(file_name, index=False)
