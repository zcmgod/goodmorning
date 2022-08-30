'''
作者：zcmgod
时间：2022/8/30
'''
from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import json
import random
import time

'''微信模板内填写
{{date.DATA}}

{{city.DATA}}
今日最高气温：{{high.DATA}}，最低气温：{{low.DATA}}
天气：{{weather.DATA}}
空气质量：{{kqzl.DATA}}
风速风向：{{fx.DATA}}({{fl.DATA}})

你已破壳{{love_days.DATA}}天啦~~
距离下一个破壳日还有{{birthday_left.DATA}}天！

今日一句：{{words.DATA}}
'''


start_date = '2022-01-01' #纪念日开始日期  格式：2022-01-01，结果位于{{love_days.DATA}}
city = '北京' #这里是北京,具体情况自定义
birthday = '01-01'#生日   格式：01-01 ，结果位于{{birthday_left.DATA}}
app_id = ''#测试公众号上的app_id
app_secret = ''#测试公众号上的app_secret
user_ids = ['','']#微信登录所在的ID
template_id = ''#模板所在的ID





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
    weather1  = json.loads(response.content.decode('utf-8').replace('var cityDZ{} ='.format(city),'').split(';var')[0])
    url = 'http://d1.weather.com.cn/sk_2d/{}.html?_='.format(city) + str(int(round(time.time() * 1000)))
    response1 = requests.get(url=url, headers=headers)
    weather = json.loads(response1.content.decode('utf-8').replace('var dataSK=',''))
    dict = {}
    dict['最低温度'] = weather1['weatherinfo']['tempn']
    dict['城市'] = weather['cityname']
    dict['最高温度'] = weather1['weatherinfo']['temp']
    dict['天气'] = weather1['weatherinfo']['weather']
    dict['空气质量指数'] = weather['aqi_pm25']
    dict['风向'] = weather1['weatherinfo']['wd']
    dict['风力'] = weather1['weatherinfo']['ws']
    return dict


def get_count():
    birthday_date = datetime.strptime(start_date, "%Y-%m-%d")
    curr_datetime = datetime.now()
    return (curr_datetime - birthday_date).days


def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    curr_datetime = datetime.now()
    return (next - curr_datetime).days+1


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

def get_date():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    week_name = week_list[int(time.strftime("%w"))-1]
    log = time.strftime("%Y-%m-%d", time.localtime()) + ' ' + week_name
    return log

client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
dict_weather = get_weather(city)
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
        "value": get_count(),
        "color": get_random_color()
    },
    "birthday_left": {
        "value": get_birthday(),
        "color": get_random_color()
    },
    "words": {
        "value": get_words(),
        "color": get_random_color()
    },
}
count = 0
for user_id in user_ids:
    res = wm.send_template(user_id, template_id, data)
    count += 1

