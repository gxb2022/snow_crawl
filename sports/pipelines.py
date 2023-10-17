# -*- coding: utf-8 -*-
import datetime
import json
import time
import redis
from scrapy.utils.project import get_project_settings


class SportsPipeline:

    def __init__(self):
        self.start_timestamp = 0
        settings = get_project_settings()
        redis_config = settings.get("REDIS_CONFIG", {})
        self.redis_client = redis.StrictRedis(**redis_config, decode_responses=True)
        self.pipe = self.redis_client.pipeline()
        self.live_set = set()
        self.today_set = set()
        self.tomorrow_set = set()
        self.bs_data_dict = {}
        self.odd_data_dict = {}
        self.score_data_dict = {}
        self.api = None
        self.ball = None
        self.ball_time = None

    def open_spider(self, spider):
        self.start_timestamp = time.time()
        self.api = spider.api
        self.ball = spider.ball
        self.ball_time = spider.ball_time

    def process_item(self, item, spider):
        detail_requests = spider.detail_requests
        bs_data = item['bs_data']
        odd_data = item['odd_data']
        score_data = item['score_data']
        bs_id = bs_data['bs_id']
        self.bs_data_dict[bs_id] = bs_data
        self.odd_data_dict[bs_id] = odd_data
        self.score_data_dict[bs_id] = score_data
        if detail_requests:
            # 存在网络延时 实时保存
            self.save_detail_data(bs_id, bs_data, odd_data, score_data)
        return item

    def save_detail_data(self, bs_id, bs_data, odd_data, score_data):
        """及时写入"""
        # 更新正常的数据
        self.pipe.hset(name=f'{self.ball}:{self.api}:bs_data', key=bs_id, value=json.dumps(bs_data))
        self.pipe.hset(name=f'{self.ball}:{self.api}:score_data', key=bs_id, value=json.dumps(score_data))
        # 记录详细数据
        self.pipe.hset(name=f'{self.ball}:{self.api}:detail_odd_data', key=bs_id, value=json.dumps(odd_data))
        self.pipe.zadd(name=f'{self.ball}:{self.api}:detail_bs_id_timestamp', mapping={bs_id: int(time.time())})
        self.pipe.execute()

    def save_data(self):
        """批量保存数据"""
        now_timestamp = int(time.time())
        for bs_id, bs_data in self.bs_data_dict.items():
            self.pipe.hset(name=f'{self.ball}:{self.api}:bs_data', key=bs_id, value=json.dumps(bs_data))
            self.pipe.zadd(name=f'{self.ball}:{self.api}:bs_id_timestamp', mapping={bs_id: now_timestamp})
        for bs_id, odd_data in self.odd_data_dict.items():
            self.pipe.hset(name=f'{self.ball}:{self.api}:odd_data', key=bs_id, value=json.dumps(odd_data))
        for bs_id, score_data in self.score_data_dict.items():
            self.pipe.hset(name=f'{self.ball}:{self.api}:score_data', key=bs_id, value=json.dumps(score_data))
        self.pipe.execute()

    def save_run_state(self, spider):
        """保存运行状态用于检查"""
        now_timestamp = time.time()
        expend_time = now_timestamp - self.start_timestamp
        # 创建一个表示时间的datetime对象，使用timestamp创建
        dt = datetime.datetime.fromtimestamp(now_timestamp)
        # 获取时区信息
        tz = dt.astimezone().tzinfo
        # 格式化可读的时间字符串，包括时区信息
        update_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        bs_data_num = len(self.bs_data_dict)
        run_state = {
            "detail_requests": spider.detail_requests,
            "ball": self.ball,
            "api": self.api,
            "ball_time": self.ball_time,
            "bs_data_num": bs_data_num,
            "update_timestamp": now_timestamp,
            "update_time": update_time,
            "expend_time": expend_time,
            "tz": str(tz)
        }
        name = f'detail_spider_state' if spider.detail_requests is True else f'spider_state'
        self.pipe.hset(name=name, key=f'{self.ball}&{self.api}&{self.ball_time}', value=json.dumps(run_state))
        spider.sports_logger.warning(f'detail_requests:{spider.detail_requests},爬虫关闭,总数量:[{bs_data_num}]')
        # 执行管道中的命令
        self.pipe.execute()

    def close_spider(self, spider):
        self.save_data()
        self.save_run_state(spider)


if __name__ == '__main__':
    test_obj = SportsPipeline()
