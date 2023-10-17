# -- coding: utf-8 --
import datetime


from sports.spiders.abc_spider import *


class BtiMinix(AbcSpider):
    api = 'bti'
    host = 'demo-light.bti.bet'
    # 测试
    host_list = ['https://demo-light.bti.bet/zh', 'prod20082-23705321.bti-SportsProject.io']

    def __init__(self, ball_time, **kwargs):
        super().__init__(ball_time, **kwargs)
        self.map_odd_field = self.get_map_odd_field()

    def start_requests(self):
        yield from self.yield_one_requests()

    def yield_one_requests(self):
        url = self.get_url()
        headers = self.get_headers()
        yield scrapy.Request(url=url, headers=headers, callback=self.parse, errback=self.handle_error)

    def get_headers(self):
        bti_cookie_path = f'{spider_path}/cookie/bti_cookie.json'
        with open(bti_cookie_path, 'r', encoding='utf-8') as f:
            cookie = json.loads(f.read())
        headers = {
            'Host': self.host,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua-mobile': '?1'
        }
        headers.update(cookie)
        return headers

    def get_url(self):
        map_ball_time = {
            "live": "live",
            "today": "prematch",
            "tomorrow": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        }
        map_sport_id = {"basketball": 2, "football": 1, "table_tennis": 26}
        sport_id = map_sport_id[self.ball]
        ball_time_str = map_ball_time[self.ball_time]
        # leagues/2/ basketball
        if self.ball_time == 'tomorrow':
            url = f'https://{self.host}/api/eventlist/asia/leagues/early/initial?' \
                  f'SportId={sport_id}&date={ball_time_str}&allEvents=false'
        else:
            url = f'https://{self.host}/api/eventlist/asia/leagues/{sport_id}/{ball_time_str}'
        return url

    def parse(self, response, **kwargs):
        raw_data = response.json()
        ball_time = response.meta.get("ball_time")
        league_data_list = raw_data.get('serializedData', [])
        self.test_save_json_data(raw_data)
        for league_data in league_data_list:
            league = league_data[8]
            bs_data_list = league_data[12]
            for one_bs_data in bs_data_list:
                item = self.item_obj()
                yield from self.handle_one_bs_data(item, one_bs_data, league=league)

    def yield_detail_requests(self, one_bs_data, item):
        bs_id = one_bs_data[0]
        all_odd_num = one_bs_data[10]
        if self.ball_time == 'tomorrow':
            return
        if self.ball == 'basketball':
            if all_odd_num < 35:
                return
        if self.ball == 'football':
            if all_odd_num < 50:
                return

        if self.detail_requests_num < 100:
            self.detail_requests_num += 1
            url = f'https://demo-light.bti.bet/api/eventpage/events/{bs_id}'
            yield scrapy.Request(
                url=url, headers=self.get_headers(), callback=self.parse_detail,
                meta={"bs_id": bs_id, "item": item},
                errback=self.handle_error
            )

    def parse_detail(self, response):
        item = response.meta.get("item")
        bs_id = response.meta.get("bs_id")
        raw_data = response.json()
        self.test_save_json_data(raw_data, bs_id=bs_id)
        data = raw_data.get("data")
        one_bs_data = data[0] if data else []
        if one_bs_data:
            item['odd_data'] = self.gen_detail_item_odd_data(one_bs_data)
            yield item

    def gen_item_bs_data(self, one_bs_data, **kwargs):
        bs_data_obj = BsData()
        bs_data_obj.api = self.api
        bs_data_obj.ball = self.ball
        bs_data_obj.ball_time = self.ball_time
        bs_data_obj.bs_id = one_bs_data[0]
        bs_data_obj.bs_time = datetime.datetime.fromisoformat(one_bs_data[3].replace("Z", "+00:00")).timestamp()
        bs_data_obj.league = kwargs.get("league")
        bs_data_obj.home_team = one_bs_data[1][0][1]['ZH']
        bs_data_obj.guest_team = one_bs_data[1][1][1]['ZH']
        return bs_data_obj

    def gen_detail_item_odd_data(self, one_bs_data):
        """xia详细数据"""
        odd_data_obj = self.odd_data_obj()
        team_data_list = one_bs_data[8]
        home_team = team_data_list[0][1]
        guest_team = team_data_list[1][1]
        home_team = ''.join(home_team.split())
        guest_team = ''.join(guest_team.split())
        # 上半场 + 全场
        odd_data = one_bs_data[20]

        for one_odd_data in odd_data:
            if one_odd_data[15] is True:  # 是否锁盘 False为没有关盘
                continue
            raw_odd_data_list = one_odd_data[13]  # 有多个
            if not raw_odd_data_list:
                continue
            raw_odd_field = one_odd_data[5][0]
            raw_name = ''.join(one_odd_data[5][1].split())
            if '队伍总得分单/双' in raw_name or '半场/全场' in raw_name:
                continue
            odd_field = None
            for model_field, raw_filed_set in self.map_odd_field.items():
                if raw_odd_field in raw_filed_set:
                    odd_field = model_field
                    break
            # 特殊处理 处理模型无法提取的odd_field 从raw_name_map里提取
            raw_name_map = {}
            if self.ball == 'basketball':
                raw_name_map = {
                    "净胜比分": 'whole_sfc',
                    "第1节净胜比分(净胜3分或更多)": 'th1_sfc',
                    "第2节净胜比分(净胜3分或更多)": 'th2_sfc',
                    "第3节净胜比分(净胜3分或更多)": 'th3_sfc',
                    "第4节净胜比分(净胜3分或更多)": 'th4_sfc',
                    "上半场净胜比分": 'half1_sfc',
                    "净胜比分七项(任一队伍)": 'whole_sfc',
                    "净胜比分十二项": 'whole_sfc',
                    f"{home_team}:队伍总得分大小盘": 'whole_ht_ou',
                    f"{home_team}:上半场队伍总得分大小盘": 'half1_ht_ou',
                    f"{home_team}:下半场队伍总得分大小盘": 'half2_ht_ou',
                    f"{home_team}:第1节队伍总得分大小盘": 'th1_ht_ou',
                    f"{home_team}:第2节队伍总得分大小盘": 'th2_ht_ou',
                    f"{home_team}:第3节队伍总得分大小盘": 'th3_ht_ou',
                    f"{home_team}:第4节队伍总得分大小盘": 'th4_ht_ou',
                    f"{guest_team}:队伍总得分大小盘": 'whole_gt_ou',
                    f"{guest_team}:上半场队伍总得分大小盘": 'half1_gt_ou',
                    f"{guest_team}:下半场队伍总得分大小盘": 'half2_gt_ou',
                    f"{guest_team}:第1节队伍总得分大小盘": 'th1_gt_ou',
                    f"{guest_team}:第2节队伍总得分大小盘": 'th2_gt_ou',
                    f"{guest_team}:第3节队伍总得分大小盘": 'th3_gt_ou',
                    f"第1节首先获得10分": 'th1_first_10',
                    f"第2节首先获得10分": 'th2_first_10',
                    f"第3节首先获得10分": 'th3_first_10',
                    f"第4节首先获得10分": 'th4_first_10',
                }
            if self.ball == 'football':
                raw_name_map = {
                    "平局退款": "whole_sf",
                    "上半场平局退款": "half1_sf",
                    "下半场平局退款": "half2_sf",
                    "角球大小盘两项": "whole_jq_ou",
                    "全场角球大小盘": "whole_jq_ou",
                    "上半场角球大小盘": "half1_jq_ou",
                    "下半场角球大小盘": "half2_jq_ou",
                    "全场角球1X2": "whole_jq_sfp",
                    "上半场角球1X2": "half1_jq_sfp",
                    "下半场角球1X2": "half2_jq_sfp",
                    "全场角球亚洲让分盘": "whole_jq_hp",
                    "上半场角球亚洲让分盘": "half1_jq_hp",
                    "下半场角球亚洲让分盘": "half2_jq_hp",
                    f"{home_team}:队伍总进球数大小盘": 'whole_ht_ou',
                    f"{guest_team}:队伍总进球数大小盘": 'whole_gt_ou',
                    f"{home_team}:上半场队伍总进球数大小盘": 'half1_ht_ou',
                    f"{guest_team}:上半场队伍总进球数大小盘": 'half1_gt_ou',
                    f"{home_team}:下半场队伍总进球数大小盘": 'half2_ht_ou',
                    f"{guest_team}:下半场队伍总进球数大小盘": 'half2_gt_ou',
                    "波胆正确比分": "whole_csb",
                    "正确比分": "whole_csb",
                    "上半场正确比分": "half2_csb",
                    "下半场正确比分": "half2_csb",
                    "进球数": "whole_tgs",
                    "上半场进球数": "half1_tgs",
                    "下半场进球数": "half2_tgs",
                    "单/双": "whole_oe",
                    "上半场单/双": "half1_oe",
                    "下半场单/双": "half2_oe",
                    "净胜比分": "whole_gd",
                    "上半场净胜比分": "half1_gd",
                    "下半场净胜比分": "half2_gd",
                }

            if not odd_field:
                odd_field = raw_name_map.get(raw_name)

            if not odd_field:
                self.sports_logger.info(
                    f'详细：无法保存在模型中,odd_field:{odd_field},raw_odd_field:{raw_odd_field},raw_name:{raw_name}'
                )
                continue

            sp_info_list = []  # 一个种类盘口多条数据
            sp_id = one_odd_data[0]

            raw_odd_data_dict = {}
            for _ in raw_odd_data_list:
                if _[13] is True:  # 是否锁盘 False为没有关盘 不确定
                    continue
                odd = _[16]
                one_sp_data = OneSpData()
                one_sp_data.sp = _[8][3]
                one_sp_data.name = _[1]["ZH"]
                one_sp_data.id = _[0]
                one_sp_data.name_id = _[9]  # 1为主队 3为客队 # p[13]:盘口值，p[6][3]：盘口赔率
                style = _[-1]
                if style in raw_odd_data_dict:
                    raw_odd_data_dict[style] = raw_odd_data_dict[style] + [(one_sp_data, odd)]
                else:
                    raw_odd_data_dict[style] = [(one_sp_data, odd)]
            for _ in raw_odd_data_dict.values():
                sp_info = SpInfo()
                sp_info.id = sp_id
                odd = _[0][1]
                sp_data_list = [i[0] for i in _]
                sp_info.odd = round(float(odd), 2) if odd else odd
                sp_info.data = sp_data_list
                sp_info_list.append(sp_info)
            setattr(odd_data_obj, odd_field, sp_info_list)

        return odd_data_obj

    def gen_item_odd_data(self, one_bs_data, **kwargs):
        odd_data_obj = self.odd_data_obj()
        # 上半场 + 全场
        odd_data = one_bs_data[8][2] + one_bs_data[8][3] if one_bs_data[13] is False else []

        for one_odd_data in odd_data:
            if one_odd_data[9] is True:  # 是否锁盘 False为没有关盘
                continue
            raw_odd_data_list = one_odd_data[7]  # 只有一个盘口数据 不用循环
            if not raw_odd_data_list:
                continue
            raw_odd_field = one_odd_data[3][0]
            raw_name = one_odd_data[3][1]
            odd_field = None
            for model_field, raw_filed_set in self.map_odd_field.items():
                if raw_odd_field in raw_filed_set:
                    odd_field = model_field
                    break
            if not odd_field:
                self.sports_logger.info(
                    f'无法保存在模型中,odd_field:{odd_field},raw_odd_field:{raw_odd_field},raw_name:{raw_name}')
                continue

            if len(raw_odd_data_list) == 3:
                sp_info_list = []  # 一个种类盘口多条数据
                sp_id = one_odd_data[0]
                odd = raw_odd_data_list[0][13]

                sp_info = SpInfo()
                sp_info.odd = round(float(odd), 2) if odd else odd

                sp_info.id = sp_id
                sp_data_list = []  # 一个种类盘口多条数据
                for _ in raw_odd_data_list:
                    if str(_[15]) != 'False':  # 是否锁盘 False为没有关盘
                        continue
                    one_sp_data = OneSpData()
                    one_sp_data.sp = _[6][3]
                    one_sp_data.name = _[2]["ZH"]
                    one_sp_data.id = _[0]
                    one_sp_data.name_id = _[7]  # 1为主队 3为客队 # p[13]:盘口值，p[6][3]：盘口赔率
                    sp_data_list.append(one_sp_data)
                sp_info = SpInfo()
                sp_info.odd = round(float(odd), 2) if odd else odd

                sp_info.id = sp_id
                sp_info.data = sp_data_list
                sp_info_list.append(sp_info)
            else:
                sp_info_list = []  # 一个种类盘口多条数据
                sp_id = one_odd_data[0]

                for i in range(0, len(raw_odd_data_list), 2):
                    # 取两个元素
                    element1 = raw_odd_data_list[i]
                    element2 = raw_odd_data_list[i + 1] if i + 1 < len(raw_odd_data_list) else None
                    if element1[15] is True or element2[15] is True:  # 是否锁盘 False为没有关盘
                        continue
                    one_sp_data1 = OneSpData()
                    one_sp_data1.sp = element1[6][3]
                    one_sp_data1.name = element1[2]["ZH"]
                    one_sp_data1.id = element1[0]
                    one_sp_data1.name_id = element1[7]  # 1为主队 3为客队 # p[13]:盘口值，p[6][3]：盘口赔率
                    one_sp_data2 = OneSpData()
                    one_sp_data2.sp = element2[6][3]
                    one_sp_data2.name = element2[2]["ZH"]
                    one_sp_data2.id = element2[0]
                    one_sp_data2.name_id = element2[7]  # 1为主队 3为客队 # p[13]:盘口值，p[6][3]：盘口赔率
                    one_sp_data_list = [one_sp_data1, one_sp_data2]
                    sp_info = SpInfo()
                    odd = element1[13]
                    sp_info.odd = round(float(odd), 2) if odd else odd
                    sp_info.id = sp_id
                    sp_info.data = one_sp_data_list
                    sp_info_list.append(sp_info)

            setattr(odd_data_obj, odd_field, sp_info_list)

        return odd_data_obj

    @classmethod
    def get_map_odd_field(cls):
        map_odd = {}
        return map_odd

    def gen_item_score_data(self, one_bs_data, **kwargs):
        pass
