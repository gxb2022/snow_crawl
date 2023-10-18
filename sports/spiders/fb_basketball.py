# -- coding: utf-8 --

from sports.spiders.fb import *


class FbBasketballSpider(FbMinix):
    ball = 'basketball'
    name = f'fb_basketball'

    item_obj = BasketballItem
    odd_data_obj = BasketballOddData
    score_data_obj = BasketballScoreData

    def gen_item_score_data(self, one_bs_data, **kwargs):
        bs_id = one_bs_data.get('id')
        score_data_obj = self.score_data_obj()
        nsg_data_list = one_bs_data.get('nsg', [])
        map_pe = {
            'whole': 3001,
            'half1': 3003,
            'half2': 3004,
            'th1': 3005,
            'th2': 3007,
            'th3': 3009,
            'th4': 3011
        }
        new_map_pe = {v: k for k, v in map_pe.items()}
        mc_data_dict = one_bs_data.get("mc", {})
        if nsg_data_list:
            pe = mc_data_dict.get("pe")
            mc_pe = new_map_pe.get(pe)  # 比赛节数
            # 3006 第一节结束
            if pe == 3006:
                mc_pe = 3005
            if pe == 3008:
                mc_pe = 3007
            if pe == 3010:
                mc_pe = 3009
            if not mc_pe:
                self.sports_logger.error(f'bs_id:{bs_id},无法提取比分pe:{pe}:{nsg_data_list},{mc_data_dict}')

            score_data_obj.score_time = ""
            score_data_obj.score_timestamp = mc_data_dict.get("s")  # 比赛节数剩余时间
            score_data_obj.period = mc_pe
        for nsg_data in nsg_data_list:
            pe = nsg_data['pe']
            sc = nsg_data['sc']
            tyg = nsg_data['tyg']
            if pe in new_map_pe and tyg == 5:
                setattr(score_data_obj, new_map_pe[pe], sc)
        return score_data_obj

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
    process.crawl(FbBasketballSpider, ball_time='live', detail_requests=True)

    # 启动爬虫
    process.start()
