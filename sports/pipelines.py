# -*- coding: utf-8 -*-
import datetime
import json
import time
import redis
from scrapy.utils.project import get_project_settings


class SportsPipeline:
    settings = get_project_settings()
    redis_config = settings.get("REDIS_CONFIG", {})
    redis_client = redis.StrictRedis(**redis_config, decode_responses=True)

    def __init__(self):
        self.start_timestamp = 0
        self.pipe = self.redis_client.pipeline()
        self.api = None
        self.ball = None
        self.ball_time = None
        self.bs_id_set = set()
        self.detail_bs_id_set = set()

    def open_spider(self, spider):
        self.start_timestamp = time.time()
        self.api = spider.api
        self.ball = spider.ball
        self.ball_time = spider.ball_time

    def process_item(self, item, spider):
        bs_data = item['bs_data']
        odd_data = item['odd_data']
        score_data = item['score_data']
        bs_id = bs_data['bs_id']
        self.bs_id_set.add(bs_id)
        # 判断是否为详细数据
        is_detail_data = dict(item).get("is_detail_data")
        if is_detail_data:
            self.detail_bs_id_set.add(bs_id)
        self.save_data_to_pipe(bs_id, bs_data, odd_data, score_data)
        if spider.detail_requests:
            self.pipe.execute()  # 存在网络延时 实时保存
        return item

    def save_data_to_pipe(self, bs_id, bs_data, odd_data, score_data):
        now_timestamp = int(time.time())
        self.pipe.hset(f'{self.ball}:{self.api}:bs_data', key=bs_id, value=json.dumps(bs_data))
        self.pipe.hset(f'{self.ball}:{self.api}:score_data', key=bs_id, value=json.dumps(score_data))
        self.pipe.hset(f'{self.ball}:{self.api}:odd_data', key=bs_id, value=json.dumps(odd_data))
        self.pipe.zadd(f'{self.ball}:{self.api}:bs_id_timestamp', mapping={bs_id: now_timestamp})
        self.pipe.zadd(f'{self.ball}:{self.api}:{self.ball_time}:bs_id_timestamp', mapping={bs_id: now_timestamp})

    def save_run_state(self, spider):
        """保存运行状态用于检查"""
        now_timestamp = time.time()
        expend_time = now_timestamp - self.start_timestamp
        dt = datetime.datetime.fromtimestamp(now_timestamp)
        tz = dt.astimezone().tzinfo
        update_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        run_state = {
            "detail_requests": spider.detail_requests,
            "ball": self.ball,
            "api": self.api,
            "ball_time": self.ball_time,
            "bs_id_num": len(self.bs_id_set),
            "detail_bs_id_num": len(self.detail_bs_id_set),
            "update_timestamp": now_timestamp,
            "update_time": update_time,
            "expend_time": expend_time,
            "tz": str(tz)
        }
        if spider.detail_requests:
            key = f"detail&{self.ball}&{self.api}&{self.ball_time}"
            _ = f'【🟢🟢🟢详细爬虫】,🟢详细数量:{len(self.detail_bs_id_set)}'
        else:
            key = f"{self.ball}&{self.api}&{self.ball_time}"
            _ = f'【普通爬虫】'
        self.pipe.hset(name=f'spiders_run_info', key=key, value=json.dumps(run_state))
        # 批量执行管道中的命令
        self.pipe.execute()
        pipe_expend_time = time.time() - now_timestamp
        spider.sports_logger.warning(f'{_},总数量:[{len(self.bs_id_set)}],爬虫耗时{expend_time},管道耗时{pipe_expend_time}')

    def close_spider(self, spider):
        self.save_run_state(spider)


if __name__ == '__main__':
    test_obj = SportsPipeline()
