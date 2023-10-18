# -- coding: utf-8 --
from sports.spiders.bti import *


class BtiFootballSpider(BtiMinix):
    ball = 'football'
    name = f'bti_football'
    item_obj = FootballItem
    odd_data_obj = FootballOddData
    score_data_obj = FootballScoreData

    @classmethod
    def get_map_odd_field(cls):

        map_odd1 = {
            'whole': {'39', '0', "200"}, 'half1': {'1', "201"}, 'half2': {"2"}
        }
        map_odd2 = {
            'sfp': 'ML',
            'hp': 'HC',
            'ou': 'OU',
        }
        map_odd = {}
        for i1, j1 in map_odd1.items():
            for i2, j2 in map_odd2.items():
                _set = {f'{j2}{j}' for j in j1}
                map_odd[f'{i1}_{i2}'] = _set

        return map_odd

    def gen_item_score_data(self, one_bs_data, **kwargs):
        score_data_obj = self.score_data_obj()
        raw_score_data: dict = one_bs_data[4][3]
        if not raw_score_data:
            return score_data_obj
        # whole
        map_score_time = {23: 'half1', 24: 'half2', 25: '中场'}

        score_data_obj.score_timestamp = one_bs_data[7][2]
        score_data_obj.period = map_score_time.get(one_bs_data[7][3])
        if one_bs_data[7][3] == 24:
            score_data_obj.period = 'whole'
        score_data_obj.whole = [int(one_bs_data[4][0]), int(one_bs_data[4][1])]
        map_score = {
            'half1': 'firstHalfScore',
            'half2': 'secondHalfScore',
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
    process.crawl(BtiFootballSpider, ball_time='live', detail_requests=True)

    # 启动爬虫
    process.start()
