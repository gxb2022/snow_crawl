# -*- coding: utf-8 -*-
import threading
import multiprocessing
import time

import redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sports.spiders.bti_football import BtiFootballSpider
from sports.spiders.fb_football import FbFootballSpider
from sports.spiders.vd_football import VdFootballSpider

from sports.spiders.bti_basketball import BtiBasketballSpider
from sports.spiders.fb_basketball import FbBasketballSpider
from sports.spiders.vd_basketball import VdBasketballSpider


class RunSpider:
    spider_class_list = [
        BtiFootballSpider,
        FbFootballSpider,
        VdFootballSpider,
        BtiBasketballSpider,
        FbBasketballSpider,
        VdBasketballSpider
    ]
    ball_time_list = [
        "live",
        "today",
        "tomorrow"
    ]

    def __init__(self):
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

    def process_function(self, spider_class, ball_time, detail_requests):
        ball_time_delay = {"live": 0.2, "today": 20, "tomorrow": 40}
        delay = ball_time_delay[ball_time]
        while True:
            p1 = multiprocessing.Process(target=self.run_spider, args=(spider_class, ball_time, detail_requests))
            p1.start()
            p1.join()
            if not detail_requests:
                time.sleep(delay)
            else:
                time.sleep(delay / 2)

    def run(self):
        threads = []
        for i in self.spider_class_list:
            for ball_time in self.ball_time_list:
                detail_list = [False, True]
                for detail in detail_list:
                    if ball_time == 'tomorrow' and detail is True:
                        continue
                    t = threading.Thread(target=self.process_function, args=(i, ball_time, detail))
                    threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()


if __name__ == "__main__":
    RunSpider().run()
