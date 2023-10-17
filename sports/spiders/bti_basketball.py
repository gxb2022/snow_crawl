# -- coding: utf-8 --
from sports.spiders.bti import *


class BtiBasketballSpider(BtiMinix):
    ball = 'basketball'
    name = f'bti_basketball'

    item = BasketballItem
    odd_data_obj = BasketballOddData
    score_data_obj = BasketballScoreData

    @classmethod
    def get_map_odd_field(cls):

        map_odd1 = {
            'whole': {'39', '0', '660', '630'},  # 详细 附加660
            'half1': {'623', '652', '2125', '631'},  # 详细 附加2125
            'half2': {'624', '2126', '632'},  # 详细 附加2126
            'th1': {'625', '654', '2129', '633'},  # 详细 附加2129
            'th2': {'655', '2046'},  # 详细 2046
            'th3': {'656'},
            'th4': {'657'}
        }
        map_odd2 = {
            'sf': 'ML',
            'hp': 'HC',
            'ou': 'OU',
            'ht_ou': None,
            'gt_ou': None,
            "oe": 'QA',
            'sfc': None,
            "first_10": None
        }
        map_odd = {}
        for i1, j1 in map_odd1.items():
            if j1 is None:
                continue
            for i2, j2 in map_odd2.items():
                if j2 is None:
                    continue
                _set = {f'{j2}{j}' for j in j1}
                map_odd[f'{i1}_{i2}'] = _set
        return map_odd

    def gen_item_score_data(self, one_bs_data, **kwargs):
        score_data_obj = self.score_data_obj()
        raw_score_data: dict = one_bs_data[4][3]
        if not raw_score_data:
            return score_data_obj
        # whole
        map_score_time = {14: 'th1', 16: 'th2', 18: 'th3', 20: 'th4'}
        setattr(score_data_obj, 'score_time', [one_bs_data[7][2], map_score_time.get(one_bs_data[7][3])])
        setattr(score_data_obj, 'whole', [int(one_bs_data[4][0]), int(one_bs_data[4][1])])
        map_score = {
            'half1': 'basketballFirstHalfScore',
            'half2': 'basketballSecondHalfScore',
            'th1': 'basketballFirstQuarterScore',
            'th2': 'basketballSecondQuarterScore',
            'th3': 'basketballThirdQuarterScore',
            'th4': 'basketballFourthQuarterScore'
        }
        for model_field, model_field_data in map_score.items():
            sc_ht = raw_score_data.get(f'{model_field_data}1', 0)
            sc_gt = raw_score_data.get(f'{model_field_data}2', 0)
            setattr(score_data_obj, model_field, [int(sc_ht), int(sc_gt)])
        return score_data_obj


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # 创建一个 CrawlerProcess 实例
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    # 实例化爬虫并添加到进程中
    process.crawl(BtiBasketballSpider, ball_time='live')

    # 启动爬虫
    process.start()
