# -- coding: utf-8 --

from sports.spiders.vd import *


class VbFootballSpider(VbMinix):
    ball = 'football'
    name = f'vb_football'

    item_obj = FootballItem
    odd_data_obj = FootballOddData
    score_data_obj = FootballScoreData

    def __init__(self, ball_time, **kwargs):
        super().__init__(ball_time, **kwargs)
        self.map_odd_field = self.get_map_odd_field()

    @classmethod
    def get_map_odd_field(cls):
        map_odd1 = {
            'whole': "", 'half1': "1st", 'half2': None
        }
        map_odd2 = {
            'sf': None,
            'sfp': "1x2",
            'hp': "ah",
            'ou': "ou",
            'oe': "oe",
            'ht_ou': "h-ou",
            'gt_ou': "a-ou",
            'jq_sfp': None,
            'jq_hp': None,
            'jq_ou': None,
            'jq_ht_ou': None,
            'jq_gt_ou': None,
            'fp_sfp': None,
            'fp_hp': None,
            'fp_ou': None,
            'csb': "cs",
            'tgs': "tg",
            'bs_gs': "btts",
            'gd': "winm",
            'first_1': None,
            'first_jq_1': None
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
        map_odd_ex = {
            "ou_1st#cr": "half1_jq_ou",
            "ah_1st#cr": "half1_jq_hp",
            "ou#cr": "whole_jq_ou",
            "ah#cr": "whole_jq_hp",
        }
        map_odd.update(map_odd_ex)
        return map_odd

    def gen_item_odd_data(self, one_bs_data, **kwargs) -> OddData():
        obj = self.odd_data_obj()
        # lp_ 最后得分 adh_ 胜负平
        # skip_field = ["t", "&", "wb", "oe#cr"]
        market = one_bs_data["market"]
        for field, field_data in market.items():
            # if [i for i in skip_field if i in field]:
            #     self.sports_logger.debug(f'放弃提取的字段：{field}')
            #     continue
            model_field = self.map_odd_field.get(field)
            if field not in self.map_odd_field:
                self.sports_logger.debug(f'无法识别字段:{field}')
                continue
            self.sports_logger.debug(f'success识别字段:{field},对应模型字段:{model_field}')
            data_list = [field_data] if isinstance(field_data, dict) else field_data
            sp_info_list = []
            for data in data_list:
                sp_info = SpInfo()
                odd = data.pop("k", None)
                data.pop("absK", None)
                sp_info.odd = self.change_odd(odd)
                sp_data_list = []
                # 'bs_gs': '双方均有进球'
                for i, j in data.items():
                    if float(j) <= 0:
                        continue
                    one_sp_data = OneSpData()
                    if 'bs_gs' in model_field:
                        j = float(j) - 1
                        one_sp_data.sp = j
                    else:
                        one_sp_data.sp = j
                    # one_sp_data.name = i # name 同id 一样
                    one_sp_data.id = i
                    sp_data_list.append(one_sp_data)
                sp_info.data = sp_data_list
                sp_info.id = field
                if sp_data_list:
                    sp_info_list.append(sp_info)
            setattr(obj, model_field, sp_info_list)
        return obj

    @classmethod
    def change_odd(cls, odd):
        parts = str(odd).split('/')
        if len(parts) == 2:
            home_handicap = float(parts[0])
            away_handicap = float(parts[1])
            sign = -1 if "-" in str(odd) else 1
            absolute_value = abs(home_handicap)
            numeric_value = (away_handicap - absolute_value) / 2 + absolute_value
            return numeric_value * sign
        else:
            return odd

    def gen_item_score_data(self, one_bs_data, **kwargs) -> ScoreData():
        obj = self.score_data_obj()
        map_period = {'1h': 'half1', "2h": "half2", "ht": "half1_end"}
        detail = one_bs_data.get("detail", {})
        if not detail:
            return obj
        period = detail["period"]
        model_period = map_period.get(period)
        if not model_period:
            self.sports_logger.error(f'无法提取score,raw_period:{period},{detail}')
            model_period = period
        obj.period = model_period
        score_time = detail.get("time")
        obj.score_time = "00:00" if not score_time else score_time
        for i, j in zip(["whole", "half1", "half2"], ["score", "ht-score", "2nd-ht-score"]):
            _ = str(detail.get(j, "")).split('-')
            if len(_) == 2:
                setattr(obj, i, _)

            obj.whole = str(detail.get("score")).split('-')
        obj.half1 = str(detail["ht-score"]).split('-')
        obj.half2 = str(detail["2nd-ht-score"]).split('-')
        return obj


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # 创建一个 CrawlerProcess 实例
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    # 实例化爬虫并添加到进程中
    process.crawl(VbFootballSpider, ball_time='today')
    # 启动爬虫
    process.start()
