# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.cookies import CookiesMiddleware, _is_public_domain
from scrapy.utils.httpobj import urlparse_cached


# useful for handling different item types with a single interface

class CustomCookiesMiddleware(CookiesMiddleware):
    def _process_cookies(self, cookies, *, jar, request):
        cookies_to_ignore = {'ak_bmsc', 'bm_sv', '__cflb', '__cf_bm', '__cflb', 'cf_clearance', 'cf_chl', 'cf_chl_1', 'cf_chl_2', '_cfuvid'}
        partial_match_to_ignore = {'visid_incap', 'incap_ses'}
        for cookie in cookies:
            if cookie.name in cookies_to_ignore:
                continue

            for partial_match in partial_match_to_ignore:
                if partial_match in cookie.name:
                    break
            else:
                cookie_domain = cookie.domain
                if cookie_domain.startswith("."):
                    cookie_domain = cookie_domain[1:]

                request_domain = urlparse_cached(request).hostname.lower()

                if cookie_domain and _is_public_domain(cookie_domain):
                    if cookie_domain != request_domain:
                        continue
                    cookie.domain = request_domain

                jar.set_cookie_if_ok(cookie, request)


class CustomProxyMiddleware(object):
    @staticmethod
    def process_request(request, spider):
        proxy_enabled = bool(spider.settings.get('HTTPPROXY_ENABLED'))
        if proxy_enabled:
            request.meta['proxy'] = spider.settings.get('HTTP_PROXY')
