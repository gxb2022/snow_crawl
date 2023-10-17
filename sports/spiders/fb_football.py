# -- coding: utf-8 --

from sports.spiders.fb import *


class FbFootballSpider(FbMinix):
    ball = 'football'
    name = f'fb_football'
    item_obj = FootballItem
    odd_data_obj = FootballOddData
    score_data_obj = FootballScoreData

    @classmethod
    def get_map_pe_mty(cls):
        map_pe = {
            'whole': 1001, 'half1': 1002, 'half2': 1003
        }
        map_mty = {
            'sf': {'1006'},
            'sfp': {'1005'},
            'hp': {'1000'},
            'ou': {'1007'},
            'oe': {'1008'},
            'ht_ou': {'1021'},
            'gt_ou': {'1022'},
            'jq_sfp': {'1009'},
            'jq_hp': {'1011'},
            'jq_ou': {'1010'},
            'jq_ht_ou': {'1057'},
            'jq_gt_ou': {'1058'},
            'fp_sfp': {'1061'},
            'fp_hp': {'1060'},
            'fp_ou': {'1063'},
            'csb': {'1099', '1100'},  # 1099 全场 1100上下半场
            'tgs': {'1101'},  # Total goals scored,
            'bs_gs': {'1027'},  # Both sides goals scored ,
            'gd': {'1018'},  # Goal difference
            'first_1': {'1089'},
            'first_jq_1': {'1094'}
        }
        return map_pe, map_mty


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # 创建一个 CrawlerProcess 实例
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    # 实例化爬虫并添加到进程中
    process.crawl(FbFootballSpider, ball_time='live')

    # 启动爬虫
    process.start()
