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

    def gen_item_score_data(self, one_bs_data, **kwargs):
        bs_id = one_bs_data.get('id')
        score_data_obj = self.score_data_obj()
        nsg_data_list = one_bs_data.get('nsg', [])
        map_pe, map_mty = self.get_map_pe_mty()

        new_map_pe = {v: k for k, v in map_pe.items()}
        mc_data_dict = one_bs_data.get("mc", {})

        if nsg_data_list:
            pe = mc_data_dict.get("pe")
            if pe == 1004:  # 足球
                pe = 1001
            mc_pe = new_map_pe.get(pe)  # 比赛节数
            if pe == 1005:
                mc_pe = f'常规时间结束{mc_pe}'
            if pe == 1010:
                mc_pe = f'点球大战{mc_pe}'
            if not mc_pe:
                print(f'bs_id:{bs_id},1检查数据是否正确pe:{pe}:nsg_data_list{nsg_data_list},mc_data_dict{mc_data_dict}')
            # 3009 3010 3011 是可能是结束 也有很大可能是其他原因
            score_data_obj.remain_timestamp_str = ""
            score_data_obj.remain_timestamp = mc_data_dict.get("s")  # 比赛节数剩余时间
            score_data_obj.period = mc_pe
        for nsg_data in nsg_data_list:
            pe = nsg_data['pe']
            sc = nsg_data['sc']
            tyg = nsg_data['tyg']
            if pe in new_map_pe and tyg == 5:
                setattr(score_data_obj, new_map_pe[pe], sc)
        return score_data_obj


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
