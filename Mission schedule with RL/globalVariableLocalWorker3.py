#satStateTable被定义为全局变量方便各个部分调用
#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from interval import Interval
import copy
#satStateTable [label storage timeWindow nextTask]

# def initsatState():
#
#     global satStateTable
#
#     satStateTable = pd.DataFrame(
#         np.zeros((1, 3)),
#         columns=['Storage','TaskNumber','label'])
#
#     satStateTable.loc[0, 'Storage'] = 5
#     satStateTable.loc[0, 'TaskNumber'] = 1
#     satStateTable.loc[0, 'label'] = 0 #状态label从零开始编号，代表不同的状态
#     # 最后的label确保了状态不会重叠编成一样的。

def initTasklist():
    # global satStateTable
    # global  Task
    # global RemainingTimeTotal
    global taskList
    # satStateTable = pd.DataFrame(
    #     np.zeros((1, 3)),
    #     columns=['Storage','TaskNumber','label'])
    taskList=[3,7,2,14,16,1,13,8,12,6,9,15,4,10,17,5,11,0]
    # Task[startTime, endTime, engergyCost, reward]


def initTask():

    global Task

    # Task = {'1': [737265.930462963, 737265.930983796, 1, 2],
    #         '2': [737265.932314815, 737265.933310185, 1, 2],
    #         '3': [737265.932569444, 737265.933460648, 1, 2],
    #         '4': [737265.933229167, 737265.934212963, 1, 2],
    #         '5': [737265.933356482, 737265.934340278, 1, 2]
    #         }

    # Task = {'1': [43305.3561578704, 43305.3571734722, 1, 2],
    #         '2': [43305.3563003472, 43305.3571645717, 1, 2],
    #         '3': [43305.356455, 43305.3571811574, 1, 2],
    #         '4': [43305.3566809838, 43305.3574698727, 1, 2],
    #         '5': [43305.3570707755, 43305.3580831713, 1, 2],
    #         '6': [43305.3574095023, 43305.3584093981, 1, 2],
    #         '7': [43305.3577584606, 43305.3587445718, 1, 2],
    #         '8': [43305.357945787, 43305.3584505324, 1, 2],
    #         '9': [43305.360321886605, 43305.361314710695, 1, 2],
    #         '10': [43305.3743262153, 43305.3753106481, 1, 2],
    #         '11': [43305.374400659704, 43305.3753651389, 1, 2],
    #         '12': [43305.375476412, 43305.3764784259, 1, 2],
    #         '13': [43305.3756235185, 43305.3765711227, 1, 2],
    #         '14': [43305.3761551273, 43305.3770963194, 1, 2],
    #         '15': [43305.4220622685, 43305.422864027794, 1, 2],
    #         '16': [43305.4230962616, 43305.4240546296, 1, 2],
    #         '17': [43305.4233630671, 43305.4241646296, 1, 2],
    #         '18': [43305.4235491667, 43305.423813541696, 1, 2],
    #         '19': [43305.4242881019, 43305.4252466667, 1, 2],
    #         '20': [43305.42438875, 43305.4253734491, 1, 2],
    #         '21': [43305.4243952778, 43305.4251186111, 1, 2],
    #         '22': [43305.4287461227, 43305.4295118056, 1, 2],
    #         '23': [43305.4292404745, 43305.4302022338, 1, 2],
    #         '24': [43305.4400880093, 43305.4410830903, 1, 2],
    #         '25': [43305.4404341898, 43305.4409515046, 1, 2],
    #         '26': [43305.4679798958, 43305.4688193171, 1, 2],
    #         '27': [43305.4689053241, 43305.4697312037, 1, 2],
    #         '28': [43305.4898499537, 43305.4908466204, 1, 2],
    #         '29': [43305.4899502083, 43305.4904528472, 1, 2],
    #         '30': [43305.491817905095, 43305.4927570602, 1, 2],
    #         '31': [43305.4925221759, 43305.4933020486, 1, 2],
    #         '32': [43305.4925519444, 43305.4933894676, 1, 2]}

    Task = {
            '3': [64, 64, 1, 100, -0.000476265673515597],
            '7': [68, 68, 1, 40, -0.000506125053969096],
            '2': [68, 68, 1, 100, 0.000452382421992215],
            '14': [118, 118, 1, 10, -0.00134238388121341],
            '16': [119, 119, 1, 10, -0.000619947849442742],
            '1': [124, 124, 1, 100, 0],
            '13': [132, 132, 1, 10, 0.000831697803189602],
            '8': [151, 151, 1, 40, -0.000189067976374232],
            '12': [210, 210, 1, 40, 0.000686616104577854],
            '6': [222, 222, 1, 100, -0.00034561912981283],
            '9': [266, 266, 1, 40, -0.000627053588052687],
            '15': [281, 281, 1, 10, -0.000249234646338898],
            '4': [313, 313, 1, 100, 0.000346407017990367],
            '10': [424, 424, 1, 40, 0.00014618739102126],
            '17': [441, 441, 1, 10, -0.000132150261068142],
            '5': [493, 493, 1, 100, -0.000143827287224467],
            '11': [493, 493, 1, 40, -0.00006707423124954]

            }
# def initRemainingTimeTotal():
#
#     global RemainingTimeTotal
#     global Task
#
#     RemainingTimeTotal = [[Interval(Task['1'][0], Task['5'][1], closed=True)]]


# def updateRemainTimeTotal(RemainingTime):
#
#     global RemainingTimeTotal
#
#     RemainingTimeTotal.append(RemainingTime)
#




# def set_value(name, value):
#
#     _global_dict[name] = value


# def addNewState(storage,nextTask,label):
#     global satStateTable
#     global Task
#
#
#
#     # Tasklist_Initial = [1, 2, 3, 4, 5, 0]
#
#
#     new = pd.DataFrame({'Storage':storage ,
#                         'TaskNumber':nextTask ,
#                         'label': label},
#                        index=[0])#设置行初始index
#
#     satStateTable = satStateTable.append(new, ignore_index=True)

def get_value_taskList():

    global taskList

    return taskList.copy()


def get_value_Task(number):

    #number为str类型数值
    global Task

    return Task[number].copy()

def get_value_TaskTotal():
    global Task

    return copy.deepcopy(Task)




# def get_value_RemainingTime(label):
#
#     global RemainingTimeTotal
#
#     RemainingTime=RemainingTimeTotal[label].copy()
#     # storage=satStateTable.loc[label, 'storage']
#     # nextTask=satStateTable.loc[label, 'nextTask']
#
#
#     return RemainingTime


# def get_value_RemainingTimeTotal():
#
#     global RemainingTimeTotal
#
#
#     # storage=satStateTable.loc[label, 'storage']
#     # nextTask=satStateTable.loc[label, 'nextTask']
#
#
#     return copy.deepcopy(RemainingTimeTotal)
#     #为了防止把地址传出去误改了，确保所有改变值的操作都在本文件的变量空间中进行
#
#
#



def get_value_satState():

    global satStateTable

    return satStateTable






def taskListMove(number):

    global taskList

    taskList.remove(number)

def taskListPop():

    global taskList

    taskList.pop(0)




