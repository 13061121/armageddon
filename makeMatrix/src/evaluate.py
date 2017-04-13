'''
处理评估数据
'''

import functools
import math
import os
import random
import re
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
import dataresolve as dr


def addtable(datatable, data):
    '''
    合并单元表格
    '''
    if datatable is None:
        return data
    else:
        return pd.concat([datatable, data], axis=1, join="outer")
        # return pd.merge(
        #     datatable,
        #     data,
        #     how="outer",
        #     on="Offset",
        #     left_index=False,
        #     right_index=False,
        #     copy=True)


def getdatas(dirpath):
    '''
    读取dirpath文件夹下面所有以.log结尾的文件中的数据并合成一个表格
    '''
    avedatatable = None
    mindatatable = None
    maxdatatable = None
    searchlist = {v: k for k, v in enumerate(config.KEYBOARDINPUTSDICT)}
    # print(searchlist)
    filelist = sorted(
        os.listdir(dirpath),
        key=
        lambda x: searchlist[x[:-4]] if x[:-4] in searchlist.keys() else -1)
    fpattern = re.compile(r'(.+)\.log')
    for file in filelist:
        filepath = dirpath + '/' + file
        if os.path.isdir(filepath) or not filepath.endswith(".log"):
            continue
        filename = fpattern.match(file).group(1)
        # print(filename)
        if os.path.isfile(filepath):
            data = dr.dowithlogfile(filepath, filename)
            avedatatable = addtable(avedatatable, data['average'])
            mindatatable = addtable(mindatatable, data['minimum'])
            maxdatatable = addtable(maxdatatable, data['maximum'])
    return {
        "average": avedatatable.fillna(0),
        "minimum": mindatatable.fillna(0),
        "maximum": maxdatatable.fillna(0)
    }


def distence(a, b):
    '''
    获得两点的欧几里得距离
    '''
    return (a - b) if a > b else (b - a)


def minindex(l):
    '''
    返回list中数值最小的值得index
    '''
    length = len(l)
    if length == 0:
        return
    (mini, minv) = (0, l[0])
    for i in range(1, length):
        if l[i] < minv:
            (mini, minv) = (i, l[i])
    return mini


def getKMeans(datas, k, precision=1):
    '''
    获得数据的k聚类
    '''
    length = len(datas)
    if length == 0:
        return None
    average = []
    for i in range(0, k):
        # print(i)
        average.append(datas[math.floor(random.random() * length)])
    pre = precision + 1
    while pre >= precision:
        matrix = []
        for i in range(0, k):
            fc = functools.partial(distence, average[i])
            matrix.append(list(map(fc, datas)))
        # 转置矩阵
        # print(matrix)
        matrix = list(map(list, zip(*matrix)))
        # print(matrix)
        indexs = list(map(minindex, matrix))
        res = [[] for i in range(0, k)]
        for i, index in enumerate(indexs):
            # print(i, index)
            res[index].append(datas[i])
        old_average = average
        average = list(map(np.average, res))
        pre = sum([distence(old_average[i], average[i]) for i in range(0, k)])
    return res


def getthreshold(data, k=2):
    '''
    获得将数据分为k个聚类的阈值，这里暂时用kMeans算法获得k=2的阈值
    '''
    data = getKMeans(data, k)
    data = sorted(data, key=np.average)
    res = []
    for i in range(1, len(data)):
        l1 = len(data[i - 1])
        l2 = len(data[i])
        if l1 > 0 and l2 > 0:
            res.append((np.max(data[i - 1]) + np.min(data[i])) / 2)
        elif l1 == 0:
            res.append(np.min(data[i]))
        else:
            res.append(np.max(data[i - 1]))
    return res


def evaluate_address(data):
    '''
    评估一个内存地址的关键性
    '''
    threshold = getthreshold(data)
    # print(threshold)
    return threshold[0]


def evaluate_address_key_value(df):
    '''

    Args:
        df: 一行数据

    Returns: ['Offset': evaluate_address(df[1:])]

    '''
    return [df[0], evaluate_address(df[1:])]


def evaluate_addresses(df: pd.DataFrame):
    '''
    评估获得的数据中所有的内存地址的关键性
    '''
    thresholds = df.apply(evaluate_address_key_value, axis=1)
    # print(thresholds)
    return thresholds


def draw_evaluate_addresses_graphes(dfs, graph_dir):
    '''
    Args:
        df: pd.DataFrame, the all table contains all the data about the calling
                frequence when every character key is pressed
        graph_dir: string, the path of directory that to store the graphes

    Returns: None

    '''
    if not os.path.exists(graph_dir) or not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)
    # print(df.columns)
    avedf = dfs['average'].T
    mindf = dfs['minimum'].T
    maxdf = dfs['maximum'].T
    # print(df)
    xcount = len(config.KEYBOARDINPUTSDICT)
    for column in avedf.columns:
        threshold = evaluate_address(avedf[column].values)
        tmp = pd.DataFrame({
            'Offset': avedf.index,
            'Average': avedf[column],
            'Minimum': mindf[column],
            'Maximum': maxdf[column],
            'Threshold': [threshold] * len(avedf.index.values)
        })
        ycount = math.ceil(avedf[column].max())
        tmp.plot(
            grid=True,
            title=column + ' Hits Count',
            xticks=range(0, xcount),
            yticks=range(0, ycount),
            secondary_y=['Maximum'],
            mark_right=False,
            rot=90)
        # plt.show()
        if avedf[column].loc[avedf[column] > threshold].count() < 5:
            print("Drawing picture of %s" % column)
            plt.savefig(os.path.join(graph_dir, column + ".png"))
        plt.clf()


if __name__ == "__main__":
    datas = getdatas("/home/larry/Documents/armageddon/makeMatrix/data")
    print(datas)
    if os.path.exists('test.db'):
        os.remove('test.db')
    conn = sqlite3.connect('test.db')
    for k, v in datas.items():
        v.to_sql(k, conn)
    draw_evaluate_addresses_graphes(datas, "../graph")
    # datas = getdatas("/home/larry/Documents/log")
    # print(datas)
    # datas.to_csv("/home/larry/Documents/log/res/res.log")
    # getKMeans([1, 2, 3, 4, 5, 6, 7, 8, 9], 2)
    # print(getthreshold([1, 2, 3, 4, 5, 10, 7, 8, 9], 2))
