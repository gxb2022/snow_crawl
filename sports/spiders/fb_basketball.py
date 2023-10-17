# -- coding: utf-8 --

from sports.spiders.fb import *


class FbBasketballSpider(FbMinix):
    ball = 'basketball'
    name = f'fb_basketball'

    item_obj = BasketballItem
    odd_data_obj = BasketballOddData
    score_data_obj = BasketballScoreData

    @classmethod
    def get_map_pe_mty(cls):
        map_pe = {
            'whole': 3001,
            'half1': 3003,
            'half2': 3004,
            'th1': 3005,
            'th2': 3006,
            'th3': 3007,
            'th4': 3008
        }
        map_mty = {
            'sf': {'3004', '3020'},
            'hp': {'3002'},
            'ou': {'3003'},
            'ht_ou': {'3012'},
            'gt_ou': {'3013'},
            "oe": {"3005"},
            'sfc': {"3027", "3007"},
            "first_10": {}
        }
        return map_pe, map_mty


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # 创建一个 CrawlerProcess 实例
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    # 实例化爬虫并添加到进程中
    process.crawl(FbBasketballSpider, ball_time='live')

    # 启动爬虫
    process.start()
