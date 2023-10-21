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
        map_period = {
            3005: 'th1',
            3006: 'th1',  # th1_end
            3007: 'th2',
            3008: 'th2',  # th2_end
            3009: 'th3',
            3010: 'th2',  # th3_end
            3011: 'th4'
        }
        mc_data_dict = one_bs_data.get("mc", {})
        if nsg_data_list:
            pe = mc_data_dict.get("pe")
            mc_pe = map_period.get(pe)  # 比赛节数
            if not mc_pe:
                self.sports_logger.error(f'bs_id:{bs_id},无法提取比分pe:{pe}:{nsg_data_list},{mc_data_dict}')
            score_data_obj.score_time = ""
            score_data_obj.score_timestamp = mc_data_dict.get("s")  # 比赛节数剩余时间
            score_data_obj.period = mc_pe

        map_score = {
            3001: 'whole',
            3003: 'half1',
            3004: 'half2',
            3005: 'th1',
            3006: 'th2',  # th1_end
            3007: 'th3',
            3008: 'th4',  # th2_end
        }
        for nsg_data in nsg_data_list:
            pe = nsg_data['pe']
            sc = nsg_data['sc']
            tyg = nsg_data['tyg']
            if pe in map_score and tyg == 5:
                setattr(score_data_obj, map_score[pe], sc)
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
