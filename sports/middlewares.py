# -*- coding: utf-8 -*-
import json
import random
import time

import redis
import requests
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.project import get_project_settings


class RedisControlMiddleware:
    hash_name = 'spiders_control'

    def __init__(self):
        settings = get_project_settings()
        redis_config = settings.get("REDIS_CONFIG", {})
        self.redis_client = redis.StrictRedis(**redis_config, decode_responses=True)

    def check_redis_key_value(self, api, ball, ball_time):
        # 使用 hget 方法获取指定哈希表中指定字段的值
        value = self.redis_client.get(f'spiders_control:{api}&{ball}&{ball_time}')
        if value:
            return True
        return False

    def process_request(self, request, spider):
        api = spider.api
        ball = spider.ball
        ball_time = spider.ball_time
        result = self.check_redis_key_value(api, ball, ball_time)
        # 在 spider_opened 方法中可以执行爬虫启动时的操作
        if result is False:
            print(f'spiders_control:{api}&{ball}&{ball_time},忽略爬虫,request{request.meta}')
            raise IgnoreRequest
        return None


class SportsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/94.0.4606.81 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/93.0.4577.82 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  Chrome/94.0.4606.81 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  Chrome/93.0.4577.82 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Edge/94.0.992.38',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Edge/93.0.961.52',
        ]
        self.request_time = 0

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers.setdefault('User-Agent', user_agent)
        if spider.detail_requests is True:
            port = random.choice([10002, 10003, 10033, 10034, 10040])
            proxy = "http:" + f'//issac-country-KR-refreshMinutes-3:' \
                              f'3df3c0-4bcaf3-c534b6-049793-4f5f41@private.residential.proxyrack.net:{port}'
            request.meta['proxy'] = proxy
        self.request_time = time.time()
        return None

    def process_response(self, request, response, spider):
        # bti 需要session才能请求通过 400响应码是正常的
        if spider.api == 'bti' and response.status in [422, 401, 403]:
            cookie = self.get_bti_cookie(spider)
            if cookie:
                user_agent = random.choice(self.user_agent_list)
                request.headers.setdefault('User-Agent', user_agent)
                request.headers.update(cookie)
                return request
        if spider.api == 'fb' and response.status == 403:
            print(f'请求错误:::::{response.text}')
        return response

    def get_bti_cookie(self, spider):
        spider.sports_logger.warning(f'Start to obtain bti cookies...')
        session = requests.session()
        url = f"https://{spider.host}/zh"
        user_agent = random.choice(self.user_agent_list)
        res = session.get(url, headers={'User-Agent': user_agent}, timeout=10)
        if res.status_code == 200:
            cookie = session.cookies.get_dict()
            with open(spider.bti_cookie_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(cookie))
            spider.sports_logger.warning(f'Success update local cookie')
        else:
            cookie = {}
            spider.sports_logger.warning(f'Fail update local cookie')
        return cookie
