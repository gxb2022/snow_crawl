# -- coding: utf-8 --

from sports.spiders.vd import *


class VbBasketballSpider(VbMinix):
    ball = 'basketball'
    name = f'vb_basketball'

    item_obj = BasketballItem
    odd_data_obj = BasketballOddData
    score_data_obj = BasketballScoreData

    def __init__(self, ball_time, **kwargs):
        super().__init__(ball_time, **kwargs)
        self.map_odd_field = self.get_map_odd_field()

    def gen_item_odd_data(self, one_bs_data, **kwargs) -> OddData():
        obj = self.odd_data_obj()
        # lp_ 最后得分 adh_ 胜负平
        skip_field = ["lp_", "adh", "oe_2h", "tmcp"]
        market = one_bs_data["market"]
        for field, field_data in market.items():
            if [i for i in skip_field if i in field]:
                self.logger.debug(f'放弃提取的字段：{field}')
                continue
            if field not in self.map_odd_field:
                self.logger.error(f'无法识别字段:{field}')
                continue
            model_field = self.map_odd_field[field]
            self.sports_logger.debug(f'success识别字段:{field},对应模型字段:{model_field}')
            data_list = [field_data] if isinstance(field_data, dict) else field_data
            sp_info_list = []
            for data in data_list:
                sp_info = SpInfo()
                odd = data.pop("k", None)
                sp_info.odd = odd
                sp_data_list = []
                for i, j in data.items():
                    one_sp_data = OneSpData()
                    one_sp_data.sp = j
                    # one_sp_data.name = i # name 同id 一样
                    one_sp_data.id = i
                    sp_data_list.append(one_sp_data)
                sp_info.data = sp_data_list
                sp_info.id = field
                sp_info_list.append(sp_info)
            setattr(obj, model_field, sp_info_list)
        return obj

    def gen_item_score_data(self, one_bs_data, **kwargs) -> ScoreData():
        obj = self.score_data_obj()
        map_odd1 = {
            '': 'whole', '1st': 'half1', '2nd': 'half2',
            'q1': 'th1',
            'q1_paused': 'th1',
            'q2': 'th2',
            'q2_paused': 'th2',
            'q3': 'th3',
            'q3_paused': 'th3',
            'q4': 'th4',
            'q4_paused': 'th4',
        }
        detail = one_bs_data.get("detail", {})
        if not detail:
            return obj
        period = detail["period"]
        model_period = map_odd1.get(period)
        if not model_period:
            print(f'无法提取model_period，period:{period}')
        obj.period = model_period
        score_time = detail.get("time")
        obj.score_time = "00:00" if not score_time else score_time
        obj.whole = str(detail.get("score")).split('-')
        obj.half1 = str(detail["1h"]).split('-')
        obj.half2 = str(detail["2h"]).split('-')
        obj.th1 = str(detail["q1"]).split('-')
        obj.th2 = str(detail["q2"]).split('-')
        obj.th3 = str(detail["q3"]).split('-')
        obj.th4 = str(detail["q4"]).split('-')
        return obj

    @classmethod
    def get_map_odd_field(cls):
        map_odd1 = {
            'whole': "",
            'half1': "1st",
            'half2': "2nd",
            'th1': "q1",
            'th2': "q2",
            'th3': "q3",
            'th4': "q4"
        }
        map_odd2 = {
            'sf': "ml",
            'hp': "ah",
            'ou': "ou",
            'ht_ou': "h-ou",
            'gt_ou': "a-ou",
            "oe": "oe",
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
                key = f"{j2}{j1}" if j1 == '' else f"{j2}_{j1}"
                value = f'{i1}_{i2}'
                map_odd[key] = value
        return map_odd


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
