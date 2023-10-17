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
            'whole': "", 'half1': None, 'half2': None
        }
        map_odd2 = {
            'sf': None,
            'sfp': "1x2",
            'hp': "ah",
            'ou': "ou",
            'oe': "oe",
            'ht_ou': None,
            'gt_ou': None,
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
            'bs_gs': None,
            'gd': None,
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
        return map_odd

    def gen_item_odd_data(self, one_bs_data, **kwargs) -> OddData():
        obj = self.odd_data_obj()
        # lp_ 最后得分 adh_ 胜负平
        skip_field = []
        market = one_bs_data["market"]
        for field, field_data in market.items():
            print(111111)
            if [i for i in skip_field if i in field]:
                self.sports_logger.debug(f'放弃提取的字段：{field}')
                continue
            model_field = self.map_odd_field.get(field)
            self.sports_logger.debug(f'success识别字段:{field},对应模型字段:{model_field}')
            if field not in self.map_odd_field:
                self.sports_logger.error(f'无法识别字段:{field}')
                continue

            continue
            data_list = [field_data] if isinstance(field_data, dict) else field_data
            sp_info_list = []
            for data in data_list:
                sp_info = SpInfo()
                odd = data.pop("k", None)

                if '/' in str(odd):
                    odd = None
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
