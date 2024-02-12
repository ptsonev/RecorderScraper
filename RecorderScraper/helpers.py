import re
from datetime import date, timedelta
from os.path import exists

import numpy as np
import pandas as pd
from dateutil.parser import parse
from pandas import DataFrame

date_columns = ['start_date', 'end_date']


def remove_non_az_digits(input_string: str) -> str:
    if not input_string:
        return ''
    return re.sub('[^a-zA-Z0-9]', '', input_string).upper()


def remove_non_az(input_string: str) -> str:
    if not input_string:
        return ''
    return re.sub('[^a-zA-Z]', '', input_string).upper()


def format_whitespaces(input_string: str, to_lower: bool = False) -> str:
    if not input_string:
        return ''
    result = re.sub(r'(&nbsp;?)|(&NBSP;?)', ' ', input_string)
    result = re.sub('\s+', ' ', result).strip()
    return result.lower() if to_lower else result


def parse_recording_date(input_date: list[str]):
    for _date in input_date:
        if not _date:
            continue
        try:
            return parse(_date).date()
        except:
            continue

    return ''


def filter_duplicates(input_list: list[str]):
    return [g for g in set(input_list) if g]


def drop_duplicates_as_string(df: DataFrame) -> DataFrame:
    df.replace({np.nan: None, '': None}, inplace=True)
    return df.loc[df.astype(str).drop_duplicates().index]


def fix_df_date_columns(df: DataFrame) -> DataFrame:
    if df is None or df.empty:
        return None
    df[date_columns] = df[date_columns].apply(pd.to_datetime, errors='coerce')
    for date_column in date_columns:
        df[date_column] = df[date_column].dt.date
    return df


def load_input_keywords_from_excel(input_excel_file_path: str, default_start_date: date = date(2000, 1, 1)) -> list[dict[str, str]]:
    # USE THIS IF THE INPUT EXCEL HAS 3 COLUMNS - keywords, start_date and end_date
    # df = pd.read_excel(input_excel_file_path, usecols=['keyword'] + date_columns)
    # df['keyword'] = df['keyword'].apply(format_whitespaces).apply(str.upper)
    # df = fix_df_date_columns(df)
    # df = drop_duplicates_as_string(df)
    # df.dropna(subset='keyword', how='all', inplace=True)
    # first_end_date_index = df[date_columns[1]].first_valid_index()
    # if first_end_date_index is None:
    #     raise Exception('Please enter at least one end_date!')
    #
    # first_start_date = (df.loc[first_end_date_index, date_columns[0]] or default_start_date)
    # first_end_date = df.loc[first_end_date_index, date_columns[1]]
    # df[date_columns[0]].fillna(value=first_start_date, inplace=True)
    # df[date_columns[1]].fillna(value=first_end_date, inplace=True)
    # return df.to_dict(orient='records')

    # USE THIS IF THE INPUT EXCEL HAS ONLY 1 COLUMN
    df = pd.read_excel(input_excel_file_path)
    df.iloc[:, 0] = df.iloc[:, 0].apply(format_whitespaces).apply(str.upper)
    df.rename(columns={df.columns[0]: 'keyword'}, inplace=True)
    df = drop_duplicates_as_string(df)
    df.dropna(subset=df.columns[0], how='all', inplace=True)

    if 'end_date' in df.columns:
        first_end_date_index = df[date_columns[1]].first_valid_index()
        start_date = df.loc[first_end_date_index, date_columns[0]].date()
        end_date = df.loc[first_end_date_index, date_columns[1]].date()
    else:
        first_day_current_month = date.today().replace(day=1)
        end_date = first_day_current_month - timedelta(days=1)
        start_date = end_date.replace(day=1)

    df['start_date'] = start_date
    df['end_date'] = end_date

    return df.to_dict(orient='records')


def load_scraped_data_from_jsonl(input_jsonl_file_path: str) -> list[dict[str, str]]:
    if not exists(input_jsonl_file_path):
        return []
    df = pd.read_json(input_jsonl_file_path, lines=True)
    if df.empty:
        return []
    elif all(column in df for column in date_columns):
        df = fix_df_date_columns(df)
        df = drop_duplicates_as_string(df)
        return df.to_dict(orient='records')
    else:
        raise Exception(f'The output data is corrupted. Please delete the file {input_jsonl_file_path}')
