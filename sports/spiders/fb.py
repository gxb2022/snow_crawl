# -- coding: utf-8 --
import math

from sports.spiders.abc_spider import *


class FbMinix(AbcSpider):
    api = 'fb'
    host = 'sportapi.fastball2.com'
    # 测试
    host_list = ['https://test.f66b88sport.com/']
    official_website = "https://test.f66b88sport.com/"

    def yield_one_requests(self, page=1):
        url = f'https://{self.host}/v1/match/getList'
        headers = self.get_headers()
        body = self.get_body(page)
        meta = {"page": page}
        yield scrapy.Request(
            url=url, body=json.dumps(body), method='POST', headers=headers,
            callback=self.parse, errback=self.handle_error, meta=meta
        )

    @classmethod
    def get_headers(cls):
        return {
            'Content-Type': 'application/json;charset=UTF-8',
            'Host': cls.host,
            'Origin': cls.official_website,
            'Referer': cls.official_website,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': "Windows",
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }

    def get_body(self, page=1):
        """sport_id 3 为篮球"""
        map_sport_id = {"basketball": 3, "football": 1, "table_tennis": 15}
        map_type = {"live": 1, "today": 3, "tomorrow": 4}
        return {
            'type': map_type[self.ball_time],
            'sportId': map_sport_id[self.ball],
            "current": page,
            "orderBy": 0,
            "isPC": 'true',
            "languageType": "CMN"
        }

    def parse(self, response, **kwargs):
        raw_data = response.json()
        page = response.meta.get("page")
        self.test_save_json_data(raw_data)
        total = raw_data.get('data', {}).get('total', 50)  # 一页50个
        size = raw_data.get('data', {}).get('size', 50)  # 当前页数量
        next_pages = math.ceil(float(total) / size)
        bs_data_list = raw_data.get('data', {}).get('records', [])
        for one_bs_data in bs_data_list:
            item = self.item_obj()
            yield from self.handle_one_bs_data(item=item, one_bs_data=one_bs_data)
        if page == 1 and next_pages > 1:  # 只有这种情况才需要下一页
            for page_num in range(2, next_pages + 1):  # 从第二页开始异步翻页
                if page_num > 8:
                    break
                yield from self.yield_one_requests(page=page_num)

    def parse_detail(self, response):
        item = response.meta.get("item")
        bs_id = response.meta.get("bs_id")
        raw_data = response.json()
        self.test_save_json_data(raw_data, bs_id=bs_id)
        one_bs_data = raw_data.get("data", {})
        if one_bs_data:
            item['is_detail_data'] = True
            item['odd_data'] = self.gen_item_odd_data(one_bs_data)
            item['score_data'] = self.gen_item_score_data(one_bs_data)
            yield item
            self.sports_logger.debug(f'解析详细请求：{bs_id}')

    def yield_detail_requests(self, one_bs_data, item):
        if self.ball_time == 'tomorrow':
            return
        tms = one_bs_data.get('tms', 0)
        hot = one_bs_data.get('lg', {}).get("hot")
        send_detail_requests = False
        max_tms = 50 if self.ball == 'football' else 35
        if self.ball_time == 'live' and hot and tms > max_tms - 15:
            send_detail_requests = True
        if tms >= max_tms:
            send_detail_requests = True
        if send_detail_requests:
            bs_id = one_bs_data.get('id')
            url = f"https://{self.host}/v1/match/getMatchDetail"
            body = {
                "languageType": "CMN",
                "matchId": bs_id
            }
            yield scrapy.Request(
                url=url,
                body=json.dumps(body),
                method='POST',
                headers=self.get_headers(),
                callback=self.parse_detail,
                meta={"bs_id": bs_id, "item": item, "detail_requests": True}
            )

    def gen_item_bs_data(self, one_bs_data, **kwargs):
        bs_data_obj = BsData()
        bs_data_obj.api = self.api
        bs_data_obj.ball = self.ball
        bs_data_obj.ball_time = self.ball_time
        bs_data_obj.bs_id = one_bs_data.get('id')
        bs_data_obj.bs_time = int(one_bs_data.get('bt')) / 1000
        bs_data_obj.league = one_bs_data.get('lg', {}).get('na')
        bs_data_obj.home_team = one_bs_data.get('ts', [])[0].get('na')
        bs_data_obj.guest_team = one_bs_data.get('ts', [])[1].get('na')
        return bs_data_obj

    def gen_item_odd_data(self, one_bs_data, **kwargs):
        odd_data_obj = self.odd_data_obj()
        odd_raw_data_list = one_bs_data.get('mg', [])
        map_pe, map_mty = self.get_map_pe_mty()
        for odd_raw_data in odd_raw_data_list:
            raw_odd_name = odd_raw_data.get('nm')  # 网页原始盘口字段名
            # skip_str_list 不提取的数据
            # skip_str_list1 = ['末位数', '赛节单双组合', '比赛会有加时-常规时间', '& 大小']
            # skip_str_list2 = ['让球胜平负', '双重机会', '零失球', '&', '精确进球数', '分钟', '半场/全场', '获胜退款']
            # skip_str_list = skip_str_list2 if self.ball == 'football' else skip_str_list1
            # if any(s in str(raw_odd_name) for s in skip_str_list):
            #     continue
            pe = odd_raw_data.get('pe')
            mty = odd_raw_data.get('mty')
            # 在map中查找 pe mty
            pe_model_field = None
            mty_model_field = None
            for field, pe_str in map_pe.items():
                if pe == pe_str:
                    pe_model_field = field
                    break
            for field, mty_set in map_mty.items():
                if str(mty) in mty_set:
                    mty_model_field = field
                    break
            if not all([pe_model_field, mty_model_field]):
                self.sports_logger.debug(
                    f'无法解析数据，{raw_odd_name},{pe_model_field, mty_model_field},{odd_raw_data}')
                continue
            sp_info_list = []  # 一个种类盘口多条数据
            mks_data_list = odd_raw_data.get('mks')
            for mks_data in mks_data_list:
                ss = mks_data.get('ss')  # 赔率是否可以下注 0无 1有
                if not ss:
                    self.logger.info(f'odd 已停止,mks_data:{mks_data}')
                    continue
                op_list = mks_data.get('op', [])
                sp_id = mks_data.get('id')
                odd = mks_data.get("li")
                # gen sp_data_list
                sp_data_list = []
                for op_data in op_list:
                    # gen one_sp_data
                    one_sp_data = OneSpData()
                    sp = round(float(op_data.get('od')) - 1, 3)  # 修复-1000情况
                    one_sp_data.sp = 0 if sp < 0 else sp
                    one_sp_data.name = op_data.get('na')
                    one_sp_data.id = op_data.get('ty')
                    sp_data_list.append(one_sp_data)

                sp_info = SpInfo()
                sp_info.odd = round(float(odd), 2) if odd else odd
                sp_info.data = sp_data_list
                sp_info.id = sp_id
                sp_info_list.append(sp_info)
            setattr(odd_data_obj, f'{pe_model_field}_{mty_model_field}', sp_info_list)
        return odd_data_obj

    def gen_item_score_data(self, one_bs_data, **kwargs):
        return self.score_data_obj()

    @classmethod
    def get_map_pe_mty(cls):
        map_pe = {
        }
        map_mty = {
        }
        return map_pe, map_mty
