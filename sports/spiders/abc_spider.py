# -*- coding: utf-8 -*-
import abc
import copy
import json
import os
import random
import time

import redis
from scrapy.utils.project import get_project_settings

from sports.items import *
from sports.logger_sports import LoggerSports
from sports.sports_model import *

# 获取当前文件所在绝对路径目录
spider_path = os.path.dirname(os.path.realpath(__file__))


class AbcSpider(scrapy.Spider, metaclass=abc.ABCMeta):
    api = None
    ball = None
    host = ''

    support_api_list = Api.get_api_list()
    support_ball_list = Ball.get_ball_list()
    support_ball_time_list = BallTime.get_ball_time_list()

    ball_time_delay = {"live": 0.2, "today": 10, "tomorrow": 20}

    item_obj = SportsItem
    odd_data_obj = OddData
    score_data_obj = ScoreData

    settings = get_project_settings()
    redis_config = settings.get("REDIS_CONFIG", {})
    # redis_client = redis.StrictRedis(**redis_config, decode_responses=True)
    redis_pool = redis.ConnectionPool(**redis_config, decode_responses=True)

    def __init__(self, ball_time="live", detail_requests=0, **kwargs):
        super().__init__(**kwargs)
        self.ball_time = ball_time
        self.detail_requests = detail_requests
        self.check_parameters()
        # 日志记录
        self.sports_logger = LoggerSports(ball=self.ball, api=self.api, ball_time=self.ball_time, level='WARNING')
        self.is_detail_requests = False
        self.delay = self.ball_time_delay[self.ball_time]

        self.start_timestamp = time.time()

    def start_requests(self):
        key = f'spiders_control:{self.ball}:{self.api}:{self.ball_time}'
        with redis.StrictRedis(connection_pool=self.redis_pool) as redis_client:
            # 执行Redis操作，字符串会被自动解码
            result = redis_client.exists(key)
        # 在 spider_opened 方法中可以执行爬虫启动时的操作
        if result == 0:
            self.sports_logger.debug(f'不存在key:{key},忽略请求...')
            time.sleep(random.randint(1, 5))
            return
        yield from self.yield_one_requests()

    @abc.abstractmethod
    def yield_one_requests(self):
        yield
        delay = self.ball_time_delay[self.ball_time]
        self.sports_logger.info(f'delay:{delay},Start one requests')
        time.sleep(delay)

    def check_parameters(self):
        if self.api not in self.support_api_list:
            raise ValueError(f'{self.api} must into {self.support_api_list}')
        if self.ball not in self.support_ball_list:
            raise ValueError(f'{self.ball} must into {self.support_ball_list}')
        if self.ball_time not in self.support_ball_time_list:
            raise ValueError(f'{self.ball_time} must into {self.support_ball_time_list}')

    def handle_one_bs_data(self, item: SportsItem, one_bs_data, **kwargs):
        item['bs_data'] = self.gen_item_bs_data(one_bs_data, **kwargs)
        item['odd_data'] = self.gen_item_odd_data(one_bs_data, **kwargs)
        item['score_data'] = self.gen_item_score_data(one_bs_data, **kwargs)
        yield item
        # 赛选需要获取详细数据的bs_id
        if self.detail_requests:
            yield from self.yield_detail_requests(one_bs_data, copy.deepcopy(item))

    @abc.abstractmethod
    def yield_detail_requests(self, one_bs_data, item: SportsItem):
        yield None

    @abc.abstractmethod
    def gen_item_bs_data(self, one_bs_data, **kwargs) -> BsData():
        """子类必须重写此函数 存储odd_data数据到BsData实例中 并返回一个BsData实例"""
        bs_data_obj = BsData()
        ...
        # 完成逻辑 从one_bs_data提取的值 存储在bs_data_obj对象中属性值中，BsData对象会自动检查值是否符合框架的要求
        ...
        return bs_data_obj

    @abc.abstractmethod
    def gen_item_odd_data(self, one_bs_data, **kwargs) -> OddData():
        """子类必须重写此函数 存储odd_data数据到OddData实例中 并返回一个OddData实例"""
        odd_data_obj = OddData()
        ...
        # 完成逻辑 从one_bs_data提取的值 存储在odd_data_obj对象中属性值中，OddData对象会自动检查值是否符合框架的要求
        ...
        return odd_data_obj

    @abc.abstractmethod
    def gen_item_score_data(self, one_bs_data, **kwargs) -> ScoreData():
        """子类必须重写此函数 存储score_data数据到ScoreData实例中 并返回一个ScoreData实例"""
        score_data_obj = ScoreData()
        ...
        # 完成逻辑 从one_bs_data提取的值 存储在score_data_obj对象中属性值中，ScoreData对象会自动检查值是否符合框架的要求
        ...
        return score_data_obj

    def test_save_json_data(self, raw_data, bs_id="ALL"):
        if bs_id:
            return
        file_name = f'{spider_path}/test_data/{self.api}_{self.ball}_{self.ball_time}_{bs_id}.json'
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(raw_data, ensure_ascii=False))

    def handle_error(self, failure):
        # 处理请求错误
        print(1111111111111111111111111111111111111111)
        request = failure.request  # 获取引发错误的请求对象
        exception = failure.value  # 获取异常信息
        proxy_ip = request.meta.get('proxy')
        print(f"detail_requests:{self.detail_requests},proxy_ip：{proxy_ip}Request:{request.url} failed : {exception}")
