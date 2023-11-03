# -*- coding: utf-8 -*-
import json

import redis
from scrapy.utils.project import get_project_settings


class PushSpiderConfig:
    """PushSuper:推送爬虫需要的请求配置参数到redis,公用类"""
    settings = get_project_settings()
    redis_config = settings.get("REDIS_CONFIG", {})
    # redis_client = redis.StrictRedis(**redis_config, decode_responses=True)
    redis_pool = redis.ConnectionPool(**redis_config, decode_responses=True)

    def push_(self, api, ball, ball_time):
        push_key = f'{api}_{ball}'
        print(push_key)
        with redis.StrictRedis(connection_pool=self.redis_pool) as redis_client:
            config = {"api": api, "ball": ball, "ball_time": ball_time}
            redis_client.lpush(push_key, json.dumps(config))


if __name__ == '__main__':
    PushSpiderConfig().push_(api="fb", ball="football", ball_time="live")
