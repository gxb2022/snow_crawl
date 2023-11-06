# Scrapy settings for SportsProject project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
COOKIES_ENABLED = False

REDIS_CONFIG = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 10,
    "password": ""
}

# SCRAPY REDIS 配置
# Scrapy Redis配置
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 指定使用的优先级队列（默认是使用'scrapy_redis.queue.SpiderPriorityQueue'）
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

REDIS_HOST = REDIS_CONFIG['host']
REDIS_PORT = REDIS_CONFIG['port']
REDIS_PARAMS = {
    'password': REDIS_CONFIG['password'],
    'db': REDIS_CONFIG["db"]
}

BOT_NAME = 'sports'

SPIDER_MODULES = ['sports.spiders']
NEWSPIDER_MODULE = 'sports.spiders'

# 启动重试2次 422响应吗需要重试 bti
RETRY_ENABLED = True
RETRY_TIMES = 1
RETRY_HTTP_CODES = [500, 503, 504, 403, 408, 429, 422]  # 重试的错误类型

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'SportsProject (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'SportsProject.middlewares.SportsSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'sports.middlewares.SportsDownloaderMiddleware': 543
}

ITEM_PIPELINES = {
    'sports.pipelines.SportsPipeline': 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'


LOG_ENABLED = True
LOG_LEVEL = 'ERROR'
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 64  # 全局最大并发数
CONCURRENT_REQUESTS_PER_DOMAIN = 32  # 单个域名最大并发数，如果下一个参数设置非0，此参数无效
CONCURRENT_REQUESTS_PER_IP = 0  # 单个ip最大并发数
DOWNLOAD_DELAY = 0  # 下载延时，高并发采集时设为0
DOWNLOAD_TIMEOUT = 12  # 超时时间设置，一般设置在10-30之间

# 禁用URL长度检查
URLLENGTH_LIMIT = 9999  # 设置一个足够大的值，以确保不会因URL长度而被忽略 vb

