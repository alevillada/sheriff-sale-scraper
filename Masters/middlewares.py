# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class MastersSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class MastersDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


from urllib.parse import urlencode
from random import randint
import requests
import logging

# Creates a new header every time
class ScrapeOpsFakeBrowserHeaderAgentMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT', 'http://headers.scrapeops.io/v1/browser-headers?') 
        self.scrapeops_fake_browser_headers_active = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        
        self._scrapeops_fake_browser_headers_enabled()
        
        if self.scrapeops_fake_browser_headers_active:
            self._get_headers_list()

    def _get_headers_list(self):
    #     payload = {'api_key': self.scrapeops_api_key}
    #     if self.scrapeops_num_results is not None:
    #         payload['num_results'] = self.scrapeops_num_results
    #     response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
    #     json_response = response.json()
    #     self.headers_list = json_response.get('result', [])
        payload = {'api_key': self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        try:
            response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
            response.raise_for_status()
            json_response = response.json()
            self.headers_list = json_response.get('result', [])
        except requests.RequestException as e:
            self.headers_list = []
            logging.error(f"Failed to fetch headers from ScrapeOps: {e}")
            
    def _get_random_browser_header(self):
        random_index = randint(0, len(self.headers_list) - 1)
        return self.headers_list[random_index]

    # testing a different implementation
    # def _scrapeops_fake_browser_headers_enabled(self):
    #     if self.scrapeops_api_key is None or self.scrapeops_api_key == '' or self.scrapeops_fake_browser_headers_active == False:
    #         self.scrapeops_fake_browser_headers_active = False
    #     else:
    #         self.scrapeops_fake_browser_headers_active = True
    
    def _scrapeops_fake_browser_headers_enabled(self):
        if not self.scrapeops_api_key or not self.scrapeops_fake_browser_headers_active:
            self.scrapeops_fake_browser_headers_active = False
    
    def process_request(self, request, spider):      
        # Skip processing if the middleware is not active
        if not self.scrapeops_fake_browser_headers_active:
            return  # Skip processing if the middleware is not active
        
        # normal processing
        random_browser_header = self._get_random_browser_header()
        
        for key, value in random_browser_header.items():
            request.headers[key] = value
        
        # request.headers['user-agent'] = random_browser_header.get('user-agent')
        # request.headers['accept'] = random_browser_header.get('accept')
        # request.headers['Accept-Encoding'] = random_browser_header.get('Accept-Encoding')
        # request.headers['accept-language'] = random_browser_header.get('accept-language')
        # request.headers['sec-ch-ua'] = random_browser_header.get('sec-ch-ua')
        # request.headers['sec-ch-ua-platform'] = random_browser_header.get('sec-ch-ua-platform')
        # request.headers['sec-fetch-mode'] = random_browser_header.get('sec-fetch-mode')
        # request.headers['sec-fetch-site'] = random_browser_header.get('sec-fetch-site')
        # request.headers['sec-fetch-user'] = random_browser_header.get('sec-fetch-user')
        
        
        
        # Checking the headers
        # print("*************** NEW HEADERS ****************\n\n")
        # print(request.headers)
        # print("\n\n********")
        
        
# ! Testing this out 
async def custom_playwright_headers(
    *,
    browser_type_name: str,
    playwright_request: 'playwright.async_api.Request',
    scrapy_request_data: dict,
) -> dict:
    """
    * This function allows you to customize the headers used by Playwright. Therefore it uses the headers from the Scrapy request (our custom headers).
    """
    # Use the headers from the Scrapy request
    scrapy_headers = scrapy_request_data['headers'].to_unicode_dict()
    
    # ! Optionally, you can modify headers further or add new ones
    # For example, ensure the User-Agent is set
    # if 'User-Agent' not in scrapy_headers:
    #     scrapy_headers['User-Agent'] = 'MyCustomUserAgent/1.0'
    
    # Return the headers to be used by Playwright
    return scrapy_headers