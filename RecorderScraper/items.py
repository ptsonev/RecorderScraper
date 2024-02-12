# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Join
from scrapy import Field

from RecorderScraper.helpers import format_whitespaces, parse_recording_date, filter_duplicates


class RecorderItem(scrapy.Item):
    keyword = Field(output_processor=TakeFirst())
    start_date = Field(output_processor=TakeFirst())
    end_date = Field(output_processor=TakeFirst())
    county = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    document_url = Field(input_processor=MapCompose(format_whitespaces), output_processor=TakeFirst())
    recording_date = Field(input_processor=MapCompose(format_whitespaces), output_processor=parse_recording_date)
    document_type = Field(input_processor=MapCompose(format_whitespaces), output_processor=Join(','))
    grantees = Field(input_processor=MapCompose(format_whitespaces, str.upper), output_processor=filter_duplicates)
    grantor = Field(input_processor=MapCompose(format_whitespaces, str.upper), output_processor=filter_duplicates)
    last_record = Field(output_processor=TakeFirst())
