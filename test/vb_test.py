import requests
from datetime import date, timedelta


def get_today_match_id(s_id, date_string):
    url = f"https://vd002-we46hc-api.gzyuanlai.com/product/business/sport/prematch/category?sid={s_id}&date={date_string}"
    payload = {}
    headers = {
        'Host': 'vd002-we46hc-api.gzyuanlai.com',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'currency': 'CNY',
        'apptype': '1',
        'accept-language': 'zh-cn',
        'sec-ch-ua-mobile': '?0',
        'time-zone': 'GMT-04:00',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'region': 'HK',
        'accept': 'application/json, text/plain, */*',
        'device': 'mobile',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://333com07.app',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://333com07.app/'
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response


def get_match_info(s_id, date_string):
    today_match_id = get_today_match_id(s_id, date_string)
    data = today_match_id["data"]
    categories = data["categories"]
    print(categories)
    today_match_id_list = []

    for tournaments_data in categories:
        tournaments = tournaments_data["tournaments"]
        for _ in tournaments:
            print(_)
            today_match_id_list.append(str(_["tid"]))
    print(today_match_id_list)
    today_match_id_str = ",".join(today_match_id_list)
    url = f"https://vd002-we46hc-api.gzyuanlai.com/product/business/sport/prematch/tournament?sid={s_id}&inplay=false&sort=kickOffTime" \
          f"&date={date_string}&tidList={today_match_id_str}"

    payload = {}
    headers = {
        'Host': 'vd002-we46hc-api.gzyuanlai.com',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'currency': 'CNY',
        'apptype': '1',
        'accept-language': 'zh-cn',
        'sec-ch-ua-mobile': '?0',
        'time-zone': 'GMT-04:00',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'region': 'HK',
        'accept': 'application/json, text/plain, */*',
        'device': 'mobile',
        'x-uuid': '4b821b6cc5bd5955f1d616f5bc1d8302',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://333com07.app',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://333com07.app/'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def get_today_match_info(s_id):
    # 获取当前日期
    current_date = date.today()
    # 将日期格式化为字符串
    date_string = current_date.strftime("%Y%m%d")
    get_match_info(s_id, date_string)


def get_morning_match_info(s_id):
    # 获取当前日期
    current_date = date.today()

    # 加一天
    next_day = current_date + timedelta(days=1)
    date_string = next_day.strftime("%Y%m%d")
    get_match_info(s_id, date_string)


def get_live_match_id(s_id):
    url = f"https://vd002-we46hc-api.gzyuanlai.com/product/business/sport/tournament/info?sid={s_id}&inplay=true&sort=tournament&language=zh-cn"

    payload = {}
    headers = {
        'Host': 'vd002-we46hc-api.gzyuanlai.com',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'currency': 'CNY',
        'apptype': '1',
        'accept-language': 'zh-cn',
        'sec-ch-ua-mobile': '?0',
        'time-zone': 'GMT-04:00',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'region': 'HK',
        'accept': 'application/json, text/plain, */*',
        'device': 'mobile',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://333com07.app',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://333com07.app/'
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response


def get_live_match_info(s_id):
    live_match_id = get_live_match_id(s_id)
    print('live_match_id',live_match_id)
    tournaments = live_match_id["data"]["tournaments"]
    live_match_id_list = []
    for matches_list in tournaments:
        matches = matches_list["matches"]
        print(matches_list)
        for _ in matches:
            print(_)
            live_match_id_list.append(str(_["iid"]))
    live_match_id_str = ",".join(live_match_id_list)
    print(f'live_match_id_str:{live_match_id_str}')
    url = f"https://vd002-we46hc-api.gzyuanlai.com/product/business/sport/match/simple?sid={s_id}&iidList={live_match_id_str}&inplay=true"
    print(url)
    payload = {}
    headers = {
        'Host': 'vd002-we46hc-api.gzyuanlai.com',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'currency': 'CNY',
        'apptype': '1',
        'accept-language': 'zh-cn',
        'sec-ch-ua-mobile': '?0',
        'time-zone': 'GMT-04:00',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'region': 'HK',
        'accept': 'application/json, text/plain, */*',
        'device': 'mobile',
        'x-uuid': '',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://333com07.app',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://333com07.app/'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


if __name__ == '__main__':
    # 足球 1  篮球 2
    s_id = "2"
    # 今日比赛
    # get_today_match_info(s_id)
    # 早盘比赛
    # get_morning_match_info(s_id)
    # 滚球比赛
    get_live_match_info(s_id)
