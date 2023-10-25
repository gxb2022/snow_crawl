# -*- coding: utf-8 -*-
import scrapy

from sports.sports_model import *


class SportsItem(scrapy.Item):
    bs_data = scrapy.Field()
    odd_data = scrapy.Field()
    score_data = scrapy.Field()
    is_detail_data = scrapy.Field()
    map_class = {}

    @classmethod
    def _clean_data(cls, key, value, value_class):
        if not isinstance(value, value_class):
            raise AttributeError(f'字段{key}的值{value}必须是{value_class}的实例')
        return value.clean_data()

    def __setitem__(self, key, value):
        if key in self.map_class:
            value = self._clean_data(key, value, self.map_class[key])
        super().__setitem__(key, value)


class BasketballItem(SportsItem):
    map_class = {
        "bs_data": BsData,
        "odd_data": BasketballOddData,
        "score_data": BasketballScoreData,
    }


class FootballItem(SportsItem):
    map_class = {
        "bs_data": BsData,
        "odd_data": FootballOddData,
        "score_data": FootballScoreData,
    }
