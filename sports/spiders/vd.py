# -- coding: utf-8 --

from datetime import timedelta, datetime

import pytz

from sports.spiders.abc_spider import *


class VbMinix(AbcSpider):
    api = 'vd'
    host = 'https://vd002-we46hc-api.gzyuanlai.com'
    # 测试
    host_list = ['vd002-we46hc-api.gzyuanlai.com']
    official_website = "https://333com07.app/"

    def __init__(self, ball_time, **kwargs):
        super().__init__(ball_time, **kwargs)
        self.iid_set = set()

    def request_iid(self):
        """每10秒获取一次iid"""
        self.iid_set.clear()
        url = self.get_url(url_style='request_league')
        headers = self.get_headers()
        self.sports_logger.info(f'Start one requests,url_style:url_style,url:{url}')
        yield scrapy.Request(url=url, headers=headers, callback=self.parse_iid)

    def request_bs(self):
        url = self.get_url(url_style='request_bs', iid_list=list(self.iid_set))
        yield scrapy.Request(url=url, headers=self.get_headers(), callback=self.parse)

    def yield_one_requests(self, page=1):
        self.sports_logger.info(f'发送请求间隔{self.delay}')
        yield from self.request_iid()

    def get_url(self, url_style='request_league', iid_list=None):
        map_sid = {"football": 1, "basketball": 2}
        sid = map_sid.get(self.ball)
        # 获取当前日期时间
        current_datetime = datetime.now()
        # 获取时间戳
        timestamp = current_datetime.timestamp()
        # 设置目标时区为GMT-04:00
        target_timezone = pytz.timezone('US/Eastern')
        # 使用目标时区转换时间戳为日期时间对象
        current_datetime_with_timezone = datetime.fromtimestamp(timestamp, tz=target_timezone)
        # 获取日期对象
        current_date = current_datetime_with_timezone.date()
        # 格式化日期为字符串
        today_string = current_date.strftime("%Y%m%d")
        tomorrow_string = (current_date + timedelta(days=1)).strftime("%Y%m%d")
        date_str = tomorrow_string if self.ball_time == 'tomorrow' else today_string
        in_play_str = "true" if self.ball_time == 'live' else "false"
        url1 = f'{self.host}/product/business/sport/tournament/info?' \
               f'sid={sid}&inplay={in_play_str}&sort=kickOffTime&language=zh-cn&date={date_str}'
        iid_list = [] if iid_list is None else iid_list
        iid_list_str = ",".join(iid_list)
        url2 = f"{self.host}/product/business/sport/match/simple?sid={sid}&iidList={iid_list_str}&inplay={in_play_str}"
        url = url1 if url_style == 'request_league' else url2
        return url

    @classmethod
    def get_headers(cls):
        return {
            'Host': 'vd002-we46hc-api.gzyuanlai.com',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'currency': 'CNY',
            'apptype': '1',
            'accept-language': 'zh-cn',
            'sec-ch-ua-mobile': '?0',
            'time-zone': 'GMT-04:00',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/117.0.0.0 Safari/537.36',
            'region': 'HK',
            'accept': 'application/json, text/plain, */*',
            'device': 'mobile',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://333com07.app',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://333com07.app/'
        }

    def parse_iid(self, response):
        self.iid_set.clear()
        raw_data = response.json()
        tournaments = raw_data.get("data", {}).get("tournaments", [])
        for matches_list in tournaments:
            matches = matches_list["matches"]
            for _ in matches:
                self.iid_set.add(str(_["iid"]))
        yield from self.request_bs()

    def parse(self, response, **kwargs):
        """子类必须重写 第一次解析"""
        raw_data = response.json()
        self.test_save_json_data(raw_data)
        bs_data_list = raw_data.get('data', {}).get('matches', [])
        for one_bs_data in bs_data_list:
            item = self.item_obj()
            yield from self.handle_one_bs_data(item=item, one_bs_data=one_bs_data)

        now_time = time.time()
        self.sports_logger.warning(f'耗时:【{now_time - self.start_time}】,delay:{self.delay},Start next requests...')
        self.start_time = now_time
        time.sleep(self.delay)
        yield from self.yield_one_requests()

    def gen_item_bs_data(self, one_bs_data, **kwargs) -> BsData():
        bs_data_obj = BsData()
        bs_data_obj.api = self.api
        bs_data_obj.ball = self.ball
        bs_data_obj.ball_time = self.ball_time
        bs_data_obj.bs_id = one_bs_data["iid"]
        bs_data_obj.bs_time = one_bs_data["kickoff"]
        bs_data_obj.league = one_bs_data["tnName"]
        bs_data_obj.home_team = one_bs_data["home"]["name"]
        bs_data_obj.guest_team = one_bs_data["away"]["name"]
        return bs_data_obj

    def gen_item_score_data(self, one_bs_data, **kwargs) -> ScoreData():
        return self.score_data_obj()

    def gen_item_odd_data(self, one_bs_data, **kwargs) -> OddData():
        obj = self.odd_data_obj()
        return obj

    def yield_detail_requests(self, one_bs_data, item: SportsItem):
        yield None
