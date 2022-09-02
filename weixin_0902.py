'''
作者：zcmgod
时间：2022/8/30
updateTime:2022/9/2
'''
from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
from borax.calendars.festivals2 import LunarFestival
from borax.calendars import LunarDate
import requests
import json
import random
import time

'''微信模板内填写
{{date.DATA}}

当前所在城市：{{city.DATA}}
最高气温：{{high.DATA}}，最低气温：{{low.DATA}}
天气：{{weather.DATA}}
空气质量：{{kqzl.DATA}}
风速风向：{{fx.DATA}}({{fl.DATA}})

你已破壳{{love_days.DATA}}天啦~~
距离下一个破壳日还有{{birthday_left.DATA}}天！

今日一则：
{{words.DATA}}
'''

app_id = ''  # 测试公众号上的app_id
app_secret = ''  # 测试公众号上的app_secret
template_id = ''  # 模板所在的ID
users = [
    {
        "user_id": "北京",
        "city": "",  # 这里是北京,具体情况自定义
        "birthday": "01-01",  # 生日   格式：01-01 ，结果位于{{birthday_left.DATA}}
        "islunar": False,  # 是否农历 True是农历 False是阳历
        "start_date": "2000-01-01",  # 纪念日开始日期  格式：2022-01-01，结果位于{{love_days.DATA}}
        "start_islunar": False,  # 是否农历 True是农历 False是阳历
    },
    {},
]  # 微信登录所在的ID


def get_weather(city):
    headers = {
        'Referer': 'http://www.weather.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    url = "http://toy1.weather.com.cn/search"
    params = {
        "cityname": city
    }
    response = requests.get(url, headers=headers, params=params, verify=False)

    city = eval(response.text)[0]['ref'].split('~')[0]
    url = 'http://d1.weather.com.cn/dingzhi/{}.html?_='.format(city) + str(int(round(time.time() * 1000)))
    headers = {
        'Referer': 'http://www.weather.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers)
    weather1 = json.loads(response.content.decode('utf-8').replace('var cityDZ{} ='.format(city), '').split(';var')[0])
    url = 'http://d1.weather.com.cn/sk_2d/{}.html?_='.format(city) + str(int(round(time.time() * 1000)))
    response1 = requests.get(url=url, headers=headers)
    weather = json.loads(response1.content.decode('utf-8').replace('var dataSK=', ''))
    dict = {}
    dict['最低温度'] = weather1['weatherinfo']['tempn']
    dict['城市'] = weather['cityname']
    dict['最高温度'] = weather1['weatherinfo']['temp']
    dict['天气'] = weather1['weatherinfo']['weather']
    dict['空气质量指数'] = weather['aqi_pm25']
    dict['风向'] = weather1['weatherinfo']['wd']
    dict['风力'] = weather1['weatherinfo']['ws']
    return dict


def get_count(start_islunar, start_date):
    if start_islunar:
        year, month, day = start_date.split('-')
        from datetime import time
        birthday_date = datetime.combine(LunarDate(int(year), int(month), int(day), 0).to_solar_date(), time())
    else:
        birthday_date = datetime.strptime(start_date, "%Y-%m-%d")
    curr_datetime = datetime.now()
    return (curr_datetime - birthday_date).days


def get_birthday_lunar(birthday):
    month, day = birthday.split('-')
    festival = LunarFestival(month=int(month), day=int(day))
    return festival.countdown()[0]


def get_birthday_Yang(birthday):
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    curr_datetime = datetime.now()
    return (next - curr_datetime).days + 1


def get_words():
    # words = requests.get("https://api.lovelive.tools/api/SweetNothings")
    # if words.status_code != 200:
    #     return get_words()
    # return words.text
    words = requests.get("https://api.shadiao.pro/chp")
    words = requests.get("https://api.shadiao.pro/du")
    # words = requests.get("https://api.shadiao.pro/pyq")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_date():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    week_name = week_list[int(time.strftime("%w")) - 1]
    log = '今天是' + time.strftime("%Y-%m-%d", time.localtime()) + ' ' + week_name + \
          '\n农历' + LunarDate.today().strftime('%Y年%L%M月%D')
    return log


def get_birthday(islunar, birthday):
    if islunar:
        return get_birthday_lunar(birthday=birthday)
    else:
        return get_birthday_Yang(birthday=birthday)


def get_poem():
    poem = requests.get('https://v1.jinrishici.com/all.json')
    if poem.status_code != 200:
        return get_poem()
    return poem.json()["content"] + '\n---《' + poem.json()["origin"] + '》' + poem.json()["author"]


def daily_today():
    daily_text = requests.get('https://api.oick.cn/lishi/api.php')
    if daily_text.status_code != 200:
        return daily_text()
    temp = daily_text.json()
    temp = temp['result']
    for i in range(len(temp) - 1):  # 倒着循环是因为历史今天是按时间顺序排的，有的事件太早了
        cur = temp[len(temp) - 1 - i]
        today_text = cur['title']
        if '世' in today_text or '出生' in today_text or '病' in today_text:
            # 如果不包含去世，离世，逝世，病逝，出生等词语，就跳出循环
            today_text = ''
            continue
        return '历史上的今天: 在' + cur['date'] + ',' + cur['title']
    return get_words()


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)

for user_list in users:
    dict_weather = get_weather(user_list['city'])
    every_text = [get_poem(), get_words(), daily_today()]
    data = {
        "date": {
            "value": get_date(),
            "color": get_random_color()
        },
        "low": {
            "value": dict_weather['最低温度'],
            "color": get_random_color()
        },
        "high": {
            "value": dict_weather['最高温度'],
            "color": get_random_color()
        },
        "city": {
            "value": dict_weather['城市'],
            "color": get_random_color()
        },
        "weather": {
            "value": dict_weather['天气'],
            "color": get_random_color()
        },
        "kqzl": {
            "value": dict_weather['空气质量指数'],
            "color": get_random_color()
        },
        "fx": {
            "value": dict_weather['风向'],
            "color": get_random_color()
        },
        "fl": {
            "value": dict_weather['风力'],
            "color": get_random_color()
        },
        "love_days": {
            "value": get_count(start_islunar=user_list['start_islunar'], start_date=user_list['start_date']),
            "color": get_random_color()
        },
        "birthday_left": {
            "value": get_birthday(islunar=user_list['islunar'], birthday=user_list['birthday']),
            "color": get_random_color()
        },
        "words": {
            "value": every_text[random.randint(0, 2)],
            #诗词，毒鸡汤，历史上的今天 随机选一个可以固定选择，替换random.randint(0, 2)就行
            "color": get_random_color()
        },
    }
    res = wm.send_template(user_list['user_id'], template_id, data)
