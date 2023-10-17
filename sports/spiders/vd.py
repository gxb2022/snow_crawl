# -- coding: utf-8 --
from datetime import date, timedelta

from sports.spiders.abc_spider import *


class VbSpider(AbcSpider):
    """"""

    def gen_item_score_data(self, one_bs_data, **kwargs) -> ScoreData():
        pass

    def gen_item_odd_data(self, one_bs_data, **kwargs) -> OddData():
        pass

    def gen_item_bs_data(self, one_bs_data, **kwargs) -> BsData():
        pass

    def yield_detail_requests(self, one_bs_data, item: SportsItem):
        pass

    api = 'vd'
    host = 'https://vd002-we46hc-api.gzyuanlai.com'
    # 测试
    host_list = ['vd002-we46hc-api.gzyuanlai.com']
    official_website = "https://333com07.app/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detail_requests_num = 0

    def yield_one_requests(self, ball_time, page=1):
        """page翻页"""
        url = self.get_url(ball_time, url_style='request_league')
        headers = self.get_headers()
        meta = {"page": page, "ball_time": ball_time}
        self.sports_logger.info(f'Start one requests,ball_time:{ball_time},page:{page},url:{url}')
        yield scrapy.Request(url=url, headers=headers, callback=self.parse_iid, meta=meta)

    def get_url(self, ball_time, url_style='request_league', iid_list=None):
        map_sid = {"football": 1, "basketball": 2}
        sid = map_sid.get(self.ball)
        current_date = date.today()
        today_string = current_date.strftime("%Y%m%d")
        tomorrow_string = (current_date + timedelta(days=1)).strftime("%Y%m%d")
        date_str = tomorrow_string if ball_time == 'tomorrow' else today_string
        in_play_str = "true" if ball_time == 'live' else "false"
        url1 = f'{self.host}/product/business/sport/tournament/info?sid={sid}&inplay={in_play_str}&sort=kickOffTime&language=zh-cn&date={date_str}'
        iid_list = [] if iid_list is None else iid_list
        iid_list_str = ",".join(iid_list)
        url2 = f"{self.host}/product/business/sport/match/simple?sid={sid}&iidList={iid_list_str}&inplay={in_play_str}"
        url = url1 if url_style == 'request_league' else url2
        print(f'url:{url}')
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
            'time-zone': 'GMT+08:00',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
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
        ball_time = response.meta["ball_time"]
        raw_data = response.json()
        print(f'raw_data:{raw_data}')
        tournaments = raw_data.get("data", {}).get("tournaments", [])
        iid_list = []
        for matches_list in tournaments:
            matches = matches_list["matches"]
            for _ in matches:
                iid_list.append(str(_["iid"]))
        print(f"iid_list:{iid_list}")
        if iid_list:
            url = self.get_url(ball_time, url_style='request_bs', iid_list=iid_list)
            yield scrapy.Request(url=url, headers=self.get_headers(), callback=self.parse)

    def parse(self, response, **kwargs):
        """子类必须重写 第一次解析"""
        print(f'比赛数据：{response.text}')
        ball_time = response.meta["ball_time"]
        raw_data = response.json()
        bs_data_list = raw_data.get('data', {}).get('matches', [])
        for one_bs_data in bs_data_list:
            item = self.item_obj()
            yield from self.handle_one_bs_data(item=item, ball_time=ball_time, one_bs_data=one_bs_data)
