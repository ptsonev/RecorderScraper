# Scrapy settings for RecorderScraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "RecorderScraper"

SPIDER_MODULES = ["RecorderScraper.spiders"]
NEWSPIDER_MODULE = "RecorderScraper.spiders"

# grantees or grantor or entity
# the data file will be saved as data_grantees.jsonl or data_grantor.jsonl
# the input file is keywords_grantees.xlsx or keywords_grantor.xlsx
# the report file is output_grantees.xlsx or output_grantor.xlsx
# SCRAPING_MODE = 'grantor'
# SCRAPING_MODE = 'grantees'
SCRAPING_MODE = 'entity'
INPUT_FILE = f'keywords_{SCRAPING_MODE}.xlsx' if SCRAPING_MODE != 'entity' else 'keywords_grantor.xlsx'
OUTPUT_FILE = f'output_{SCRAPING_MODE}.xlsx' if SCRAPING_MODE != 'entity' else 'output_grantor.xlsx'
DATA_FILE = f'data_{SCRAPING_MODE}.jsonl'

DOWNLOAD_TIMEOUT = 60

AUTOTHROTTLE_ENABLED = False
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 50
CONCURRENT_REQUESTS_PER_DOMAIN = 1

LOGSTATS_INTERVAL = 10
LOG_LEVEL = 'INFO'
LOG_SHORT_NAMES = False
STATS_DUMP = True

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

HTTPPROXY_ENABLED = False
HTTP_PROXY = 'http://127.0.0.1:8888'

TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

DOWNLOADER_MIDDLEWARES = {
    "RecorderScraper.middlewares.CustomProxyMiddleware": 100,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 101,
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": None,
    "RecorderScraper.middlewares.CustomCookiesMiddleware": 700,
}

FEEDS = {
    DATA_FILE: {
        'format': 'jsonlines',
        'overwrite': False,
        'encoding': 'utf8'
    }
}

HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [400, 401, 402, 403, 405, 406, 407, 408, 429, 500, 501, 502, 503, 504]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
