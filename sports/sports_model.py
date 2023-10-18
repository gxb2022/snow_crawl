# -*- coding: utf-8 -*-


class Api:
    """下面变量顺序不能改变影响逻辑"""
    fb = "FB"
    bti = "BTI"
    pm = ""
    vd = ""

    @classmethod
    def get_api_list(cls):
        """返回排序后的列表"""
        return ["fb", "bti", "pm", "vd"]


class Ball:
    football = "Football"
    basketball = "Basketball"
    table_tennis = ""

    @classmethod
    def get_ball_list(cls):
        """返回排序后的列表"""
        return ["football", "basketball"]


class BallTime:
    live = ""
    today = ""
    tomorrow = ""

    @classmethod
    def get_ball_time_list(cls):
        """返回排序后的列表"""
        return ["live", "today", "tomorrow"]


class OneSpData:
    sp = 1.8
    name = "大"
    id = None
    name_id = None

    def __setattr__(self, name, value):
        # 必须要走通下面所有逻辑
        if name == 'sp':
            value = round(float(value), 3)  # 统一强制转换成float 并保留3位小数
        if name == 'name':
            value = str(value).strip()  # 统一强制转换成字符串并去除前后空格

        super().__setattr__(name, value)


class SpInfo:
    data = [OneSpData, OneSpData]
    id = None
    odd = None

    @classmethod
    def __change_odd(cls, odd):
        try:
            return round(float(odd), 2)
        except TypeError:
            return odd
        except ValueError:
            return odd

    def __setattr__(self, name, value):
        if name == 'odd':
            value = self.__change_odd(value)
        if name == 'data':
            if not isinstance(value, list):
                raise TypeError(f"data字段 必须要是一个列表,而不是{type(value)}")
            if not all(isinstance(_, OneSpData) for _ in value):
                raise ValueError(f"data字段值 列表里的值必须都是 {OneSpData} 的实例对象")
            value = [one_sp_data.__dict__ for one_sp_data in value]
        super().__setattr__(name, value)


class BsData:
    api = None
    ball = None
    ball_time = None
    bs_id = None
    bs_time = None  # 10位时间戳
    league = None
    home_team = None
    guest_team = None

    def __setattr__(self, name, value):
        # 必须要走通下面所有逻辑
        if name == 'api':
            if not hasattr(Api, value):
                raise ValueError(f"api字段的值 必须是类{Api}的属性")
        if name == 'ball':
            if not hasattr(Ball, value):
                raise ValueError(f"ball字段的值 必须是类{Ball}的属性")
        if name == 'ball_time':
            if not hasattr(BallTime, value):
                raise ValueError(f"ball_time字段的值 必须是类{BallTime}的属性")
        if name in ['bs_id', 'league', 'home_team', 'guest_team']:
            value = str(value).strip()  # 统一强制转换成字符串并去除前后空格
        if name == 'bs_time':  # 时间转换后再进来
            if len(str(int(value))) != 10:
                raise TypeError(f"bs_time字段值必须为10位整数时间戳,value:{value}")
            value = int(value)

        super().__setattr__(name, value)

    @classmethod
    def __result_filed_list(cls):
        return [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")]

    def clean_data(self) -> dict:
        """清洗数据并校验数据为标准格式"""
        result_filed_list = self.__result_filed_list()
        result_data = {field: self.__dict__.get(field) for field in result_filed_list}
        if not all(result_data.values()):
            raise ValueError(f'result_data的值必须全部为真,result_data:{result_data}')
        return result_data


class OddData:
    map_odd = {}

    def __setattr__(self, name, value):

        if name not in self.map_odd:
            raise AttributeError(f"不能添加属性值 '{name}', 支持的属性值为: {list(self.map_odd)}")
        if not isinstance(value, list):
            raise TypeError(f"字段 '{name}' 的值必须要是一个列表,而不是{type(value)},value:{value}")
        if not all(isinstance(_, SpInfo) for _ in value):
            raise ValueError(f"字段 '{name}' 的列表值里的元素必须都是 {SpInfo} 的实例对象")
        value = [sp_info.__dict__ for sp_info in value]
        super().__setattr__(name, value)

    def clean_data(self) -> dict:
        """清洗数据并校验数据为标准格式"""
        # 只保留值为真的
        result_data = {k: v for k, v in self.__dict__.items() if v}
        if not all(result_data.values()):
            raise ValueError(f'result_data的值必须全部为真,result_data:{result_data}')
        return result_data


class BasketballOddData(OddData):
    map_odd_1 = {
        'whole': '全场', 'half1': '上半场', 'half2': '下半场',
        'th1': '第1节', 'th2': '第2节', 'th3': '第3节', 'th4': '第4节'
    }
    map_odd_2 = {
        'sf': '胜负', 'hp': '让分', 'ou': '大小', 'ht_ou': '主队-大小', 'gt_ou': '客队-大小', "oe": "单双",
        'sfc': "胜分差", "first_10": "首先获得10分"
    }
    map_odd = {}
    for odd_1, i in map_odd_1.items():
        for odd_2, j in map_odd_2.items():
            map_odd[f'{odd_1}_{odd_2}'] = f'{i}-{j}'


class FootballOddData(OddData):
    map_odd_1 = {
        'whole': '全场', 'half1': '上半场', 'half2': '下半场'
    }
    map_odd_2 = {
        'sf': '胜负(平局退款)',
        'sfp': '胜负平',
        'hp': '让分',
        'ou': '大小',
        'oe': '单双',
        'ht_ou': '主队大小',
        'gt_ou': '客队大小',
        'jq_sfp': '角球胜负平',
        'jq_hp': '角球让分',
        'jq_ou': '角球大小',
        'jq_ht_ou': '角球主队大小',
        'jq_gt_ou': '角球客队大小',
        'fp_sfp': '罚牌胜负平',
        'fp_hp': '罚牌让分',
        'fp_ou': '罚牌大小',
        'csb': '波胆',  # correct socre betting,
        'tgs': '总进球数',  # Total goals scored,
        'bs_gs': '双方均有进球',  # Both sides goals scored ,
        'gd': '净胜球数',  # Goal difference
        'first_1': '第1粒进球',
        'first_jq_1': '第1个角球'
    }
    for n in range(1, 10):
        map_odd_2[f'first_{n}'] = f'第{n}粒进球'
        map_odd_2[f'first_jq_{n}'] = f'第{n}个角球'

    map_odd = {}
    for odd_1, i in map_odd_1.items():
        for odd_2, j in map_odd_2.items():
            map_odd[f'{odd_1}_{odd_2}'] = f'{i}_{j}'


class ScoreData:
    period = "当前时期"
    score_timestamp = "剩下时间戳"
    score_time = "当前时期剩余时间"

    @classmethod
    def seconds_to_time(cls, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f'{minutes:02d}:{seconds:02d}'

    @classmethod
    def time_string_to_seconds(cls, time_str):
        try:
            minutes, seconds = map(int, time_str.split(":"))
            total_seconds = minutes * 60 + seconds
            return total_seconds
        except ValueError:
            return time_str

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

    def clean_data(self) -> dict:
        """清洗数据并校验数据为标准格式"""
        # 只保留值为真的
        result_data = {k: v for k, v in self.__dict__.items() if v or v == 0}
        if 'score_time' not in result_data and 'score_timestamp' in result_data:
            score_timestamp = result_data.get("score_timestamp")
            result_data["score_time"] = self.seconds_to_time(score_timestamp)
        if 'score_timestamp' not in result_data and 'score_time' in result_data:
            score_time = result_data.get("score_time")
            result_data["score_timestamp"] = self.time_string_to_seconds(score_time)
        new_result_data = {}
        for i, j in result_data.items():
            if isinstance(j, list):
                v = [int(_) for _ in j if str(_).isdigit()]
            else:
                v = j
            if v or v == 0:
                new_result_data[i] = v
        return new_result_data


class BasketballScoreData(ScoreData):
    whole = '全场'
    half1 = '上全场'
    half2 = '下全场'
    th1 = '第1节'
    th2 = '第2节'
    th3 = '第3节'
    th4 = '第4节'


class FootballScoreData(ScoreData):
    # map_period = {1002: 'half1', 1003: "half1_end", 1004: "half2"}
    score_time = '比分时间'
    whole = '全场'
    half1 = '上全场'
    half2 = '下全场'
