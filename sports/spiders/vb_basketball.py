# -- coding: utf-8 --

from sports.items import BasketballItem
from sports.spiders.vd import VbSpider
from sports.sports_model import BasketballOddData, BasketballScoreData


class VbBasketballSpider(VbSpider):
    ball = 'basketball'
    name = f'vb_basketball'

    item = BasketballItem
    odd_data_obj = BasketballOddData
    score_data_obj = BasketballScoreData


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # 创建一个 CrawlerProcess 实例
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    # 实例化爬虫并添加到进程中
    process.crawl(VbBasketballSpider, ball_time='live')

    # 启动爬虫
    process.start()
