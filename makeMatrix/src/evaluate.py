'''
处理评估数据
'''

import functools
import os
import random
import re

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
import dataresolve as dr
import database as db


def addtablerows(datatable, data):
    '''
    合并单元格
    '''
    if datatable is None:
        return data
    else:
        return pd.concat([datatable, data], join='outer')


def addtablecolumns(datatable, data):
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


def gethistogram(conn):
    '''
    获取所有地址的数据分分布图
    注意：SQL语言中select语句会合并同类项
    '''
    maxhitcount = 350
    datas = pd.Series([0] * maxhitcount, index=range(0, maxhitcount))
    for tablename in config.KEYBOARDINPUTSDICT:
        data = db.readcolumndatafromcursor(db.readcursor(conn, tablename), 2)
        for v in data:
            datas[v] = datas[v] + 1
    return datas


def draw_histogram(datas, pngfilepath=None):
    '''
    将datas绘制直方图
    '''
    datas.plot(grid=True, logx=False)
    newdatas = pd.Series([0.0] * datas.count(), index=datas.index)
    datasum = datas.sum()
    print(datasum)
    count = 0
    for index in datas.index:
        count += datas[index]
        newdatas[index] = count * 1.0 / datasum
    print(newdatas)
    newdatas.plot(secondary_y=True, mark_right=True)
    if pngfilepath is not None:
        plt.savefig(pngfilepath)
    else:
        plt.show()
    plt.clf()


def getdatas(dirpath, conn):
    '''
    读取dirpath文件夹下面所有以.log结尾的文件中的数据并存储在数据库conn中
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
            # 存储原始数据
            data['original'].to_sql(file[:-4], conn)
            avedatatable = addtablecolumns(avedatatable, data['average'])
            mindatatable = addtablecolumns(mindatatable, data['minimum'])
            maxdatatable = addtablecolumns(maxdatatable, data['maximum'])
    avedatatable.fillna(0).to_sql('average', conn)
    mindatatable.fillna(0).to_sql('minimum', conn)
    maxdatatable.fillna(0).to_sql('maximum', conn)


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


def draw_address_hits_graph(dfs, title, graphpath=None):
    '''
    绘制Hits分布图
    '''
    tmpdf = pd.DataFrame({
        'KBchar':
        dfs['KBchar'].map(config.KEYBOARDINPUTSDICT.index),
        'Hits':
        dfs['Hits']
    })
    tmpdf.plot(
        kind="scatter",
        x='KBchar',
        y='Hits',
        title=title,
        xticks=range(0, len(config.KEYBOARDINPUTSDICT)),
        grid=True,
        rot=90).set_xticklabels(config.KEYBOARDINPUTSDICT)
    if graphpath is None:
        plt.show()
    else:
        plt.savefig(graphpath)
    plt.clf()


def get_address_hits_data(conn, address):
    '''
    获取某一地址的分布数据
    '''
    datas = None
    dataslength = 1
    for c in config.KEYBOARDINPUTSDICT:
        cursor = db.readcursor(conn, c, condition="Offset='" + address + "'")
        data = db.readcolumndatafromcursor(cursor, 2)
        # print(data)
        length = len(data)
        rows = pd.DataFrame(
            {
                'KBchar': [c] * length,
                "Hits": data
            },
            index=range(dataslength, dataslength + length))
        dataslength += length
        datas = addtablerows(datas, rows)
    return datas


def draw_evaluate_addresses_graphes(conn,
                                    line_graph_dir,
                                    scatter_graph_dir=None):
    '''
    Args:
        df: pd.DataFrame, the all table contains all the data about the calling
                frequence when every character key is pressed
        graph_dir: string, the path of directory that to store the graphes

    Returns: None

    '''
    if not os.path.exists(line_graph_dir) or not os.path.isdir(line_graph_dir):
        os.makedirs(line_graph_dir)
    if scatter_graph_dir is not None and (
            not os.path.exists(scatter_graph_dir) or
            not os.path.isdir(scatter_graph_dir)):
        os.makedirs(scatter_graph_dir)
    # print(df.columns)
    avedf = db.read_sql_table('average', conn).reindex(
        columns=config.KEYBOARDINPUTSDICT).T
    mindf = db.read_sql_table('minimum', conn).reindex(
        columns=config.KEYBOARDINPUTSDICT).T
    maxdf = db.read_sql_table('maximum', conn).reindex(
        columns=config.KEYBOARDINPUTSDICT).T
    # print(df)
    xcount = len(config.KEYBOARDINPUTSDICT)
    for column in avedf.columns:
        threshold = evaluate_address(avedf[column].values)
        t = avedf[column].loc[avedf[column] > threshold].count()
        if t >= 2 or t == 0:
            continue
        tmp = pd.DataFrame({
            'Offset': avedf.index,
            'Average': avedf[column],
            'Minimum': mindf[column],
            'Maximum': maxdf[column],
            'Threshold': [threshold] * len(avedf.index.values),
            # 'Threshold-L': [threshold] * len(avedf.index.values),
            # 'Threshold-R': [threshold] * len(avedf.index.values)
        })
        # ycount = math.ceil(avedf[column].max())
        ycount = math.ceil(maxdf[column].max())
        tmp.plot(
            grid=True,
            title=column + ' Hits Count',
            xticks=range(0, xcount),
            yticks=range(0, ycount, math.ceil(ycount / 30)),
            # secondary_y=['Maximum', 'Threshold-R'],
            # mark_right=False,
            rot=90)
        # plt.show()
        print("Drawing picture of %s" % column)
        plt.savefig(os.path.join(line_graph_dir, column + ".png"))
        plt.clf()
        if scatter_graph_dir is not None:
            draw_address_hits_graph(
                get_address_hits_data(conn, column),
                column + ' Hits Count Distribution',
                os.path.join(scatter_graph_dir, column + ".png"))


if __name__ == "__main__":
    conn = db.initdatabase("test.db", False)
    # getdatas("/home/larry/Documents/armageddon/makeMatrix/data", conn)
    draw_evaluate_addresses_graphes(conn, "../graph", "../graph/scatter")
    conn.close()
    # datas = getdatas("/home/larry/Documents/log")
    # print(datas)
    # datas.to_csv("/home/larry/Documents/log/res/res.log")
