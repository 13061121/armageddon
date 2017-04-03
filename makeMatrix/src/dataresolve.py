#! /usr/bin/python3
'''
resolve data file
'''
import os
import re
import traceback
import pandas as pd
import numpy as np


def pretreatment(filepath, outfilepath):
    '''
    预处理文件
    '''
    read_file = open(filepath, "r")
    write_file = open(outfilepath, "w")
    fpattern = re.compile(r'(0x[a-f0-9]+) - ([0-9]+)')
    # print(fpattern)
    write_file.write("Offset,Hits\n")
    for line in read_file:
        line = line.replace("Offset,Hits\n", "")
        # print(line)
        line = fpattern.findall(line)
        if len(line) == 0:
            continue
        else:
            # print(line)
            write_file.write(line[0][0] + ',' + line[0][1] + '\n')
    read_file.close()
    write_file.close()


def readlogfile(filepath, filename):
    '''
    read datas from file
    '''
    try:
        print("Evaluate log file: " + filename)
        dfs = pd.read_csv(
            filepath, sep=',', dtype={"Offset": np.str,
                                      "Hits": np.int64})
        offsets = dfs['Offset'].drop_duplicates()
        count = offsets.count()
        # print(count)
        dfd = pd.DataFrame({
            filename: pd.Series([0] * count),
            'Offset': offsets
        })
        # print(dfd.columns)
        for offset in offsets:
            count = dfs[dfs['Offset'] == offset]["Hits"].mean()
            dfd.loc[dfd.Offset == offset, filename] = count
        dfd = dfd.dropna()
        dfd.reset_index(inplace=True)
        dfd.drop(['index'], axis=1, inplace=True)
        return dfd
    except Exception as ex:
        print(Exception, ex)
        traceback.print_exc()
        return None


def dowithlogfile(filepath, filename):
    '''
    do with file
    '''
    tmp_file_path = "./tmp.log"
    pretreatment(filepath, tmp_file_path)
    res = readlogfile(tmp_file_path, filename)
    os.remove(tmp_file_path)
    return res


if __name__ == "__main__":
    # dowithlogfile("../data/a.log",'a')
    dowithlogfile("/home/larry/Documents/log/space.log", "space")
