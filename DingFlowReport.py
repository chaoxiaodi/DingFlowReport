import requests, time
import json, sys, re, os
import pymysql
import datetime
import random
from pyecharts import options as opts
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType
from collections import Counter
from pyecharts.charts import Geo
from pyecharts.faker import Faker
from pyecharts.globals import ChartType, SymbolType

class DingFlowReport:
    '''
    获取钉钉审批状态并分析出报表发送到钉钉机器人
    '''
    def __init__(self):
        self.CorpId = "dingding corpid"
        self.AppKey = "dingding app key"
        self.AppSecret = "dingding app secret"

    # 获取钉钉Token，返回Token
    def getToken(self):
        durl = "https://oapi.dingtalk.com/gettoken?appkey=%s&appsecret=%s" %(self.AppKey, self.AppSecret)
        result = requests.get(durl).json()
        # print(result["access_token"])
        return result["access_token"]

    # 根据时间、审批类型、发起人等获取审批实例列表
    def getFlowList(self, dToken):
        durl = "https://oapi.dingtalk.com/topapi/processinstance/listids?access_token=%s" %(dToken)
        '''
        补卡审批process_code：PROC-62617DF2-885D-4144-BD64-A0A9E1F504E2
        出差审批process_code：PROC-12C5623C-501F-47EE-90DF-7D0500D6B588
        '''
        data = {
            "process_code": "PROC-12C5623C-501F-47EE-90DF-7D0500D6B588",
            "start_time": "1559318400000",
            "end_time": "1577808000000",
            "size": 20,
            "userid_list": ("1856312148650082")
        }
        result = requests.post(durl, data=json.dumps(data, ensure_ascii=False))
        return result.json()["result"]["list"]

    #根据实例出差id返回实例详情--截止到2019年年底
    def getFlowInstance(self, dToken, process_list=[]):
        durl = "https://oapi.dingtalk.com/topapi/processinstance/get?access_token=%s" % (dToken)
        cc_city_list = []
        for i in process_list:
            city_set = ()
            data = {
                "process_instance_id": i
            }
            result = requests.post(durl, data=json.dumps(data, ensure_ascii=False))
            cfcity = \
            json.loads(json.loads(result.json()["process_instance"]["form_component_values"][3]["value"])[1]["value"])[
                0]["rowValue"][2]["value"]
            ddcity = \
            json.loads(json.loads(result.json()["process_instance"]["form_component_values"][3]["value"])[1]["value"])[
                0]["rowValue"][3]["value"]
            city_set = (cfcity, ddcity)
            cc_city_list.append(city_set)
        # 返回出差城市集合列表
        return cc_city_list

    # 计算返回的城市列表城市数量
    def calc_city_list(self, city_list=[]):
        fcity_list = [y for x in city_list for y in x]
        numcity = Counter(fcity_list)
        return numcity

    # 地图线路测试
    def map_line_test(self, num_city_list=[], city_list=[]):
        c = (
            Geo(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="800px"))
            .add_schema(maptype="china")
            .add(
                "",
                num_city_list,
                type_=ChartType.EFFECT_SCATTER,
                color="blue",
            )
            .add(
                "2019下半年出差路线图",
                city_list,
                type_=ChartType.LINES,
                effect_opts=opts.EffectOpts(
                    symbol=SymbolType.TRIANGLE, symbol_size=6, color="Lime"
                ),
                linestyle_opts=opts.LineStyleOpts(curve=0.3, color="green"),
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title="出差路线图"))
        )
        return c

    def testlist(self):
        list11 = [('北京', '天津'), ('北京', '武汉'), ('北京', '北京'), ('北京', '南京'), ('北京', '武汉'), ('北京', '上海'), ('北京', '石家庄'), ('北京', '武汉'), ('北京', '武汉'), ('北京', '苏州'), ('北京', '威县'), ('北京', '天津'), ('北京', '包头')]
        return list11

if __name__ == '__main__':
    w = DingFlowReport()
    dtoken = w.getToken()
    city_list = w.testlist()
    process_list = w.getFlowList(dtoken)
    city_list = w.getFlowInstance(dtoken, process_list)
    num_city_list = w.calc_city_list(city_list).most_common(100)
    print(city_list, num_city_list)
    ccmap= w.map_line_test(num_city_list, city_list)
    ccmap.render()



