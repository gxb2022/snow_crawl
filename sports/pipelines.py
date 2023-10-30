# -*- coding: utf-8 -*-

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
        self.save_data_to_pipe(bs_id, bs_data, odd_data, score_data)
        spider.sports_logger.info(f'bs_id:{bs_id},已保存')
        return item

    def save_data_to_pipe(self, bs_id, bs_data, odd_data, score_data):
        now_timestamp = int(time.time())
        self.pipe.hset(f'{self.ball}:{self.api}:bs_data', key=bs_id, value=json.dumps(bs_data))
        self.pipe.hset(f'{self.ball}:{self.api}:score_data', key=bs_id, value=json.dumps(score_data))
        self.pipe.hset(f'{self.ball}:{self.api}:odd_data', key=bs_id, value=json.dumps(odd_data))
        self.pipe.zadd(f'{self.ball}:{self.api}:bs_id_data', mapping={bs_id: now_timestamp})
        self.pipe.zadd(f'{self.ball}:{self.api}:{self.ball_time}:bs_id_data', mapping={bs_id: now_timestamp})
        self.pipe.execute()  # 存在网络延时 实时保存


if __name__ == '__main__':
    test_obj = SportsPipeline()
