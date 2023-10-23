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
        if detail_requests:
            # 存在网络延时 实时保存
            self.save_data_to_pipe(bs_id, bs_data, odd_data, score_data)
            self.pipe.execute()
        else:
            self.save_data_to_pipe(bs_id, bs_data, odd_data, score_data)
        self.bs_id_set.add(bs_id)
        return item

    def save_data_to_pipe(self, bs_id, bs_data, odd_data, score_data):
        now_timestamp = time.time()
        self.pipe.hset(f'{self.ball}:{self.api}:{self.ball_time}:bs_data', key=bs_id, value=json.dumps(bs_data))
        self.pipe.hset(f'{self.ball}:{self.api}:{self.ball_time}:score_data', key=bs_id, value=json.dumps(score_data))
        self.pipe.hset(f'{self.ball}:{self.api}:{self.ball_time}:odd_data', key=bs_id, value=json.dumps(odd_data))
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
            "bs_data_num": len(self.bs_id_set),
            "update_timestamp": now_timestamp,
            "update_time": update_time,
            "expend_time": expend_time,
            "tz": str(tz)
        }
        name = f'detail_spiders_state' if spider.detail_requests is True else f'spiders_state'
        self.pipe.hset(name=name, key=f'{self.api}&{self.ball}&{self.ball_time}', value=json.dumps(run_state))
        # 执行管道中的命令
        self.pipe.execute()

    def close_spider(self, spider):
        self.save_run_state(spider)
        expend_time = time.time() - self.start_timestamp
        spider.sports_logger.warning(
            f'爬虫关闭,detail:{spider.detail_requests},总数量:[{len(self.bs_id_set)}],耗时：{expend_time}'
        )


if __name__ == '__main__':
    test_obj = SportsPipeline()
