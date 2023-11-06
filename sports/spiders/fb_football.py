# -- coding: utf-8 --

from sports.spiders.fb import *


class FbFootballSpider(FbMinix):
    ball = 'football'
    name = f'fb_football'
    redis_key = f'fb_football'
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

    def gen_item_score_data(self, one_bs_data, **kwargs):
        map_period = {1002: 'half1', 1003: "half1_end", 1004: "half2"}
        score_data_obj = self.score_data_obj()
        nsg_data_list = one_bs_data.get('nsg', [])
        if not nsg_data_list:
            return score_data_obj
        bs_id = one_bs_data.get('id')
        mc_data_dict = one_bs_data.get("mc", {})
        pe = mc_data_dict.get("pe")
        period = map_period.get(pe)  # 比赛节数
        if not period:
            self.sports_logger.debug(
                f'bs_id:{bs_id},1检查数据是否正确pe:{pe}:{nsg_data_list},{mc_data_dict}')
        score_data_obj.score_timestamp = mc_data_dict.get("s")  # 比赛节数剩余时间
        score_data_obj.period = period
        _score_map = {1001: 'whole', 1002: 'half1', 1003: 'half2'}
        for nsg_data in nsg_data_list:
            pe = nsg_data['pe']
            sc = nsg_data['sc']
            tyg = nsg_data['tyg']
            if pe in _score_map and tyg == 5:
                setattr(score_data_obj, _score_map[pe], sc)
        return score_data_obj


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # 创建一个 CrawlerProcess 实例
    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)
    # 实例化爬虫并添加到进程中
    process.crawl(FbFootballSpider, ball_time='tomorrow', detail_requests=0)
    # 启动爬虫
    process.start()
