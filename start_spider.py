# -*- coding: utf-8 -*-
import threading
import multiprocessing
import time

import redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sports.spiders.bti_football import BtiFootballSpider
from sports.spiders.fb_football import FbFootballSpider
from sports.spiders.vb_football import VbFootballSpider

from sports.spiders.bti_basketball import BtiBasketballSpider
from sports.spiders.fb_basketball import FbBasketballSpider
from sports.spiders.vb_basketball import VbBasketballSpider


class RunSpider:
    def __init__(self, spider_class_list):
        self.spider_class_list = spider_class_list
        redis_config = get_project_settings().get("REDIS_CONFIG", {})
        self.redis_client = redis.StrictRedis(**redis_config, decode_responses=True)

    @classmethod
    # 定义运行爬虫的函数
    def run_spider(cls, spider_class, ball_time, detail_requests):
        settings = get_project_settings()
        process = CrawlerProcess(settings=settings)
        process.crawl(spider_class, ball_time=ball_time, detail_requests=detail_requests)
        process.start()
        process.stop()
        ball_time_delay = {"live": 1, "today": 10, "tomorrow": 30}
        time.sleep(ball_time_delay.get(ball_time, 1))

    def process_function(self, spider_class, ball_time, detail_requests):
        while True:
            # key_exists = self.redis_client.exists("allow_spider")
            # if not key_exists:
            #     print(f'爬虫无需运行....', spider_class, ball_time, detail_requests)
            #     time.sleep(1)
            #     continue
            # 创建两个新的子进程来同时运行爬虫
            p1 = multiprocessing.Process(target=self.run_spider, args=(spider_class, ball_time, detail_requests))
            p1.start()
            p1.join()

    def run(self):
        threads = []
        for i in self.spider_class_list:
            # for j in ['live', 'today', 'tomorrow']:
            for j in ['live']:
                detail_list = [False] if i.api == 'vd' else [False]
                for detail in detail_list:
                    t = threading.Thread(target=self.process_function, args=(i, j, detail))
                    threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()


if __name__ == "__main__":
    _ = [
        BtiFootballSpider, FbFootballSpider, VbFootballSpider,
        BtiBasketballSpider, FbBasketballSpider, VbBasketballSpider
    ]
    RunSpider(_).run()
