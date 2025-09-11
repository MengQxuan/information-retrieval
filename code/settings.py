BOT_NAME = "nk_search"

SPIDER_MODULES = ["nk_search.spiders"]
NEWSPIDER_MODULE = "nk_search.spiders"

# 不遵守 robots.txt
ROBOTSTXT_OBEY = False

# 下载延迟设置为 0（更快）
DOWNLOAD_DELAY = 0.15

DEPTH_LIMIT = 100 # 允许爬取的最大深度为 30

# 并发配置
CONCURRENT_REQUESTS = 32  # 最大并发请求数量
CONCURRENT_REQUESTS_PER_DOMAIN = 16  # 单域并发请求数限制
# CONCURRENT_REQUESTS_PER_IP = 16  # 每个 IP 的最大并发请求数（默认0，无限制）


AUTOTHROTTLE_ENABLED = True  # 启用自动限速
AUTOTHROTTLE_START_DELAY = 0.5  # 初始下载延迟（秒）
AUTOTHROTTLE_MAX_DELAY = 3  # 最大下载延迟（秒）
AUTOTHROTTLE_TARGET_CONCURRENCY = 16  # 每秒钟请求的目标并发数
AUTOTHROTTLE_DEBUG = False  # 开启调试模式


# 输出编码和 CSV 文件格式
FEED_EXPORT_ENCODING = "utf-8-sig"

# 数据存储位置 (CSV 格式)
FEEDS = {
    "output.csv": {
        "format": "csv",
        "encoding": "utf-8-sig",
        "fields": ["title", "url", "text", "linksurl"],
    }
}

# 请求头 (伪装成浏览器)
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en",
}

# ITEM_PIPELINES = {
#     "nk_search.pipelines.MySQLPipeline": 300,  # 数字表示执行顺序，越小优先级越高
# }

# # 增加爬取和处理的超时时间
# DOWNLOAD_TIMEOUT = 10

# # 添加重试机制
# RETRY_ENABLED = True
# RETRY_TIMES = 2

# LOG_LEVEL = 'ERROR'

# DOWNLOADER_MIDDLEWARES = {
#     "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
# }
# DOWNLOADER_MIDDLEWARES = {
#     "scrapy_proxy_pool.middlewares.ProxyPoolMiddleware": 610,
#     "scrapy_proxy_pool.middlewares.BanDetectionMiddleware": 620,
# }
