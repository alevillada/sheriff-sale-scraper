# Scrapy settings for Masters project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# ! Playwright-Scrapy integration
import os

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_LAUNCH_OPTIONS = {
        "headless": True,
        "devtools": True,
    } 

LOG_LEVEL = 'DEBUG' # Temporary

# * custom headers for Playwright
PLAYWRIGHT_PROCESS_REQUEST_HEADERS = 'Masters.middlewares.custom_playwright_headers'

# ! End of Playwright-Scrapy integration

BOT_NAME = "Masters"

SPIDER_MODULES = ["Masters.spiders"]
NEWSPIDER_MODULE = "Masters.spiders"


# ! ScrapeOps settings
SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT = 'https://headers.scrapeops.io/v1/user-agents'
SCRAPEOPS_FAKE_USER_AGENT_ENABLED = True 
SCRAPEOPS_NUM_RESULTS = 50
SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT = 'https://headers.scrapeops.io/v1/browser-headers'
SCRAPEOPS_FAKE_BROWSER_HEADER_ENABLED = True # this is the setting that enables the middleware

# ! End of ScrapeOps settings

# * custom playright context settings
# PLAYWRIGHT_CONTEXTS = {
#     "persistent": {
#         "user_data_dir": "./data",  # will be a persistent context
#         'java_script_enabled': True,
#     },
# }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "Masters (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "Masters.middlewares.MastersSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # "Masters.middlewares.MastersDownloaderMiddleware": 543,
    "Masters.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware": 300,
    # "Masters.middlewares.RedirectMiddleware": 400,
    # "Masters.middlewares.ScrapeOpsPlaywrightUserAgentMiddleware": 100,
}

# ! I can set this globally or per spider
# ! custom settings for throttle
CONCURRENT_REQUESTS = 4
REDIRECT_MAX_TIMES = 1
COOKIES_ENABLED = True
RETRY_ENABLED = True
RETRY_TIMES = 2 

# DOWNLOAD_DELAY = 5  # Delay in seconds between requests
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0

# ! end of custom settings for throttle

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# ! Pipeline
ITEM_PIPELINES = {
   "Masters.pipelines.MastersPipeline": 300, # pipeline
   "Masters.pipelines.SaveToPostgresPipeline": 400 # database
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
