#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.05.18
    @author: jhbae
'''
import re
from time import localtime, strftime

def schedule_valid_check(a_schedule_time):
    b_char_check= False
    for s_cron_type in a_schedule_time:

        s_time_table = a_schedule_time[s_cron_type]
        if s_time_table is not None or len(s_time_table) > 1:
            if s_cron_type == 'min':
                for i_min_decimal_cnt in re.findall('\d+', s_time_table):
                    if len(i_min_decimal_cnt) > 2 or int(i_min_decimal_cnt) > 59:
                        return '[%s] %s 값이 잘못지정되었습니다. "* 혹은 0~59" 기준내에 입력해주세요.' %(s_time_table, s_cron_type.upper())
            elif s_cron_type == 'hour':
                for i_hour_decimal_cnt in re.findall('\d+', s_time_table):
                    if len(i_hour_decimal_cnt) > 2 or int(i_hour_decimal_cnt) > 23:
                        return '[%s] %s 값이 잘못지정되었습니다.  "* 혹은  0~23" 기준내에 입력해주세요.' %(s_time_table, s_cron_type.upper())
            elif s_cron_type == 'day':
                for i_day_decimal_cnt in re.findall('\d+', s_time_table):
                    if len(i_day_decimal_cnt) > 2 or int(i_day_decimal_cnt) > 31:
                        return '[%s] %s 값이 잘못지정되었습니다.  "* 혹은 1~31" 기준내에 입력해주세요.' %(s_time_table, s_cron_type.upper()) 

            elif s_cron_type == 'month':
                for i_month_decimal_cnt in re.findall('\d+', s_time_table):
                    if len(i_month_decimal_cnt) > 2 or int(i_month_decimal_cnt) > 12:
                        return '[%s] %s 값이 잘못지정되었습니다.  "* 혹은 1~12" 기준내에 입력해주세요.' %(s_time_table, s_cron_type.upper())

            elif s_cron_type == 'weekday':
                for i_month_decimal_cnt in re.findall('\d+', s_time_table):
                    if len(i_month_decimal_cnt) > 1 or int(i_month_decimal_cnt) > 7:
                        return '[%s] %s 값이 잘못지정되었습니다.  "* 혹은 1~7" 기준내에 입력해주세요.' %(s_time_table, s_cron_type.upper())                 

            if bool(re.search(r"([a-zA-Z\s\'\^\+\?\.\(\)\|\{\}\[\"])", s_time_table)):
                b_char_check = False
            else:
                if bool(re.search('[0-9\*\,\-]', s_time_table)):
                    if bool(re.search(',$',s_time_table)):
                        b_char_check = False
                    elif bool(re.match('^\*$', s_time_table)):
                        b_char_check = True
                    elif bool(re.match('^\*\/[0-9]{1,2}$', s_time_table)):
                        b_char_check = True
                    elif bool(re.match('^[0-9]{1,2}$', s_time_table)):
                        b_char_check = True
                    elif bool(re.match('^[0-9]{1,2},',s_time_table)):
                        b_char_check = True
                    elif bool(re.match('^[0-9]{1,2}\-[0-9]{1,2}\/[0-9]{1,2}$',s_time_table)):
                        b_char_check = True
                    elif bool(re.match('^[0-9]{1,2}\-[0-9]{1,2}$',s_time_table)):
                        b_char_check = True
    if not b_char_check:
        s_rtn_msg = '지정된 스케쥴 형식에 맞지 않습니다.'
        return s_rtn_msg

    return b_char_check


def schedule_operation(a_schedule_time):
    if a_schedule_time['min'] == '*':
        s_min = strftime('%M',localtime())
    else:
        s_min = a_schedule_time['min']
        a_minutes = s_min.split('/')
        if len(a_minutes) > 1:
            s_min_res = int(strftime('%M',localtime())) % int(a_minutes[1])
            if s_min_res == 0:
                s_min = strftime('%M',localtime())
            else:
                s_min = a_minutes[1]

    if a_schedule_time['hour'] == '*':
        s_hour = strftime('%H',localtime())
    else:
        s_hour = a_schedule_time['hour']
        a_hours = s_hour.split('/')
        if len(a_hours) > 1:
            s_hour_res = int(strftime('%H',localtime())) % int(a_hours[1])
            if s_hour_res == 0:
                s_hour = strftime('%H',localtime())
            else:
                s_hour = a_hours[1]

    if a_schedule_time['day'] == '*':
        s_day = strftime('%d',localtime())
    else:
        s_day = a_schedule_time['day']
        a_days = s_day.split('/')
        if len(a_days) > 1:
            s_day_res = int(strftime('%d',localtime())) % int(a_days[1])
            if s_day_res == 0:
                s_day = strftime('%d',localtime())
            else:
                s_day = a_days[1]

    if a_schedule_time['month'] == '*':
        s_month = strftime('%m',localtime())
    else:
        s_month = a_schedule_time['month']
        a_months = s_month.split('/')
        if len(a_months) > 1:
            s_month_res = int(strftime('%m',localtime())) % int(a_months[1])
            if s_month_res == 0:
                s_month = strftime('%m',localtime())
            else:
                s_month = a_months[1]

    if a_schedule_time['weekday'] == '*':
        s_weekday = strftime('%w',localtime())
    else:
        s_weekday = a_schedule_time['weekday']
        a_weekdays = s_weekday.split('/')
        if len(a_weekdays) > 1:
            s_weekday_res = int(strftime('%w',localtime())) % int(a_weekdays[1])
            if s_weekday_res == 0:
                s_weekday = strftime('%w',localtime())
            else:
                s_weekday = a_weekdays[1]

    s_min = "%02d" %int(s_min)
    s_hour = "%02d" %int(s_hour)
    s_day = "%02d" %int(s_day)
    s_month = "%02d" %int(s_month)
    s_weekday = "%01d" %int(s_weekday)

    s_execute_time = s_min + s_hour + s_day + s_month + s_weekday

    if strftime('%M%H%d%m%w') == s_execute_time:
        b_res = True
    else:
        b_res = False
    return b_res

def schedule_check(s_check_schedule):
    a_schedule_time = {}

    a_time_format = ['min','hour','day','month','weekday']
    a_schedule_split = s_check_schedule.split(' ')

    if len(a_schedule_split) == 5:
        i_cnt = 0
        for a_schedule_value_list in a_schedule_split:
            a_schedule_value = a_schedule_value_list.split(',')
            if len(a_schedule_value) < 2:
                a_schedule_time[a_time_format[i_cnt]] = a_schedule_value[0]
            else:
                for a_schedule_val_array in a_schedule_value:
                    if a_time_format[i_cnt] == 'min':
                        if strftime('%M',localtime()) == a_schedule_val_array:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                            break
                        else:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                    if a_time_format[i_cnt] == 'hour':
                        if strftime('%H',localtime()) == a_schedule_val_array:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                            break
                        else:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                    if a_time_format[i_cnt] == 'day':
                        if strftime('%d',localtime()) == a_schedule_val_array:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                            break
                        else:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array

                    if a_time_format[i_cnt] == 'month':
                        if strftime('%m',localtime()) == a_schedule_val_array:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                            break
                        else:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                            break

                    if a_time_format[i_cnt] == 'weekday':
                        if strftime('%w',localtime()) == a_schedule_val_array:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
                            break
                        else:
                            a_schedule_time[a_time_format[i_cnt]] = a_schedule_val_array
            i_cnt= i_cnt+1
        b_res = schedule_operation(a_schedule_time)
    return b_res

