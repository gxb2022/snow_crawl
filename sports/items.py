# -*- coding: utf-8 -*-
import scrapy

from sports.sports_model import *


class SportsItem(scrapy.Item):
    bs_data = scrapy.Field()
    odd_data = scrapy.Field()
    score_data = scrapy.Field()

    @classmethod
    def _clean_data(cls, key, value, value_class):
        if not isinstance(value, value_class):
            raise AttributeError(f'字段{key}的值{value}必须是{value_class}的实例')
        return value.clean_data()


class BasketballItem(SportsItem):

    def __setitem__(self, key, value):
        map_class = {
            "bs_data": BsData,
            "odd_data": BasketballOddData,
            "score_data": BasketballScoreData,
        }
        if key in self.fields:
            value = self._clean_data(key, value, map_class[key])
        super().__setitem__(key, value)


class FootballItem(SportsItem):

    def __setitem__(self, key, value):
        map_class = {
            "bs_data": BsData,
            "odd_data": FootballOddData,
            "score_data": FootballScoreData,
        }
        if key in self.fields:
            value = self._clean_data(key, value, map_class[key])
        super().__setitem__(key, value)
