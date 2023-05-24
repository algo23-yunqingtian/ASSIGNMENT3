# -*- coding: utf-8 -*-
"""
Created on Wed May 24 20:28:38 2023

@author: dell
"""

import tushare as ts
import datetime

def get_SD(one_list):
    average = sum(one_list)/len(one_list)
    result = 0
    for one_num in one_list:
        result += (one_num - average) ** 2
    result = (result / len(one_list)) ** (1/2)
    return result

token = '此处输入你的token'
pro = ts.pro_api(token)


date = pro.trade_cal(start_date='20180101',end_date=datetime.datetime.today().strftime('%Y%m%d'))
date = list(date[date.is_open==1]['cal_date'].values)
date1 = date[-400:-200] # 前半段数据时间段
date2 = date[-200:] # 后半段数据时间段
df1 = pro.moneyflow_hsgt(start_date=date1[0],end_date=date1[-1])  # 单次请求限制为300条
df2 = pro.moneyflow_hsgt(start_date=date2[0],end_date=date2[-1])

# 1)构建北上资金的开盘日期列表total_north_date
north_date1 = list(df1['trade_date'].values)
north_date1.reverse() # 调整为时间升序
north_date2 = list(df2['trade_date'].values)
north_date2.reverse() # 调整为时间升序
for i in north_date2:
    north_date1.append(i)
total_north_date = north_date1

# 2）构建北上资金的所有净买入额列表total_north_money
north_money1 = list(df1['north_money'].values)
north_money1.reverse()    # 调整为时间升序
north_money2 = list(df2['north_money'].values)
north_money2.reverse()    # 调整为时间升序
for i in north_money2:
    north_money1.append(i)
total_north_money = north_money1


signal = '无信号' # 防止历史内没有信号导致报错
print('\n历史信号:'
     f'\n(起始判断日期为{total_north_date[252]})\n')
for i in range(252,len(total_north_money)):
    north_money = total_north_money[i-252:i+1]
    average = sum(north_money)/len(north_money)
    SD = get_SD(north_money) # 标准差
    up_line = float(format((average + SD * 1.5) * 0.01, '.4f')) # 看多线，保留4位小数位数
    down_line = float(format((average - SD * 1.5) * 0.01, '.4f')) # 看空线，保留4位小数位数
    current_north_money = float(format(north_money[-1] * 0.01, '.4f')) # 切片中的最近期值，保留4位小数
    current_north_date = total_north_date[i] # 该最近期值所对应的日期
    if current_north_money >= up_line:
        signal = '看多'
        print('<看多>',current_north_date,
             f'看多线:{up_line}亿元, 看空线:{down_line}亿元, 北上净买入:{current_north_money}亿元')
    if current_north_money <= down_line:
        signal = '看空'
        print('<看空>',current_north_date,
             f'看多线:{up_line}亿元, 看空线:{down_line}亿元, 北上净买入:{current_north_money}亿元')

    if i == len(total_north_money)-1:
        print(f'\n最新数据:{current_north_date}'
              f'\n看多线:{up_line}亿元'
              f'\n看空线:{down_line}亿元'
              f'\n最新北上净买入:{current_north_money}亿元')
        if current_north_money >= up_line:
            print('\n出现做多信号！！！')
            print('\n积极入市！！！')
        elif current_north_money <= down_line:
            print('\n出现做空信号！！！')
            print('\n注意仓位！！！')
        else:
            print(f'\n未出现多空信号，维持当前<{signal}>阶段')