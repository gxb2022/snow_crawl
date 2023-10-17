# -*- coding: utf-8 -*-

import threading
import time
import multiprocessing

import redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sports.spiders.bti_basketball import BtiBasketballSpider
from sports.spiders.bti_football import BtiFootballSpider
from sports.spiders.fb_basketball import FbBasketballSpider
from sports.spiders.fb_football import FbFootballSpider

redis_config = get_project_settings().get("REDIS_CONFIG", {})
redis_client = redis.StrictRedis(**redis_config, decode_responses=True)


# 定义运行爬虫的函数
def run_spider(spider_class, ball_time, detail_requests):
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    process.crawl(spider_class, ball_time=ball_time, detail_requests=detail_requests)
    process.start()
    process.stop()
    ball_time_delay = {"live": 1, "today": 10, "tomorrow": 30}
    time.sleep(ball_time_delay.get(ball_time, 1))


def process_function(spider_class, ball_time, detail_requests):
    while True:
        key_exists = redis_client.exists("allow_spider")
        if not key_exists:
            print(f'爬虫无需运行....')
            time.sleep(1)
            continue
        # 创建两个新的子进程来同时运行爬虫
        p1 = multiprocessing.Process(target=run_spider, args=(spider_class, ball_time, detail_requests))
        p1.start()
        p1.join()


if __name__ == "__main__":

    spider_class_list = [FbBasketballSpider, BtiBasketballSpider, BtiFootballSpider, FbFootballSpider]
    ball_time_list = ['live', 'today', 'tomorrow']

    threads = []
    for i in spider_class_list:
        for j in ball_time_list:
            t = threading.Thread(target=process_function, args=(i, j, True))
            threads.append(t)
            t = threading.Thread(target=process_function, args=(i, j, False))
            threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
