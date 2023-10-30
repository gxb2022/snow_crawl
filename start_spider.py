import time
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sports.spiders.fb_basketball import FbBasketballSpider
from sports.spiders.fb_football import FbFootballSpider
from sports.spiders.vb_basketball import VbBasketballSpider
from sports.spiders.vb_football import VbFootballSpider


class RunSpider:
    spider_class_list = [
        FbFootballSpider, VbFootballSpider,
        FbBasketballSpider, VbBasketballSpider
    ]
    ball_time_list = ['live', 'today', 'tomorrow']
    detail_requests_list = [False, True]

    def run_spider(self, spider_class, ball_time, detail_requests):
        _delay = 1 if detail_requests else 0
        time.sleep(_delay)
        settings = get_project_settings()
        process = CrawlerProcess(settings=settings)
        process.crawl(spider_class, ball_time=ball_time, detail_requests=detail_requests)
        process.start()

    def run(self):
        processes = []
        for spider_class in self.spider_class_list:
            for ball_time in self.ball_time_list:
                for detail_requests in self.detail_requests_list:
                    process = Process(target=self.run_spider, args=(spider_class, ball_time, detail_requests))
                    processes.append(process)
                    process.start()

        for process in processes:
            process.join()


if __name__ == "__main__":
    runner = RunSpider()
    runner.run()
