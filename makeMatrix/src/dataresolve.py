#! /usr/bin/python3
'''
resolve data file
'''
import os
import re
import traceback

import numpy as np
import pandas as pd

import config


def pretreatment(filepath, outfilepath):
    '''
    预处理文件
    '''
    # read_file = open(filepath, "r")
    write_file = open(outfilepath, "w")
    fpattern = re.compile(r'(0x[a-f0-9]+) - ([0-9]+)')
    # print(fpattern)
    with open(filepath, "r") as read_file:
        rescontent = []
        write_file.write("Offset,Hits\n")
        for line in read_file:
            line = line.replace("Offset,Hits\n", "")
            # print(line)
            line = fpattern.findall(line)
            if len(line) == 0:
                continue
            else:
                # print(line)
                # write_file.write(line[0][0] + ',' + line[0][1] + '\n')
                # 过滤掉部分较小的数据
                if int(line[0][1]) > 20:
                    rescontent.append(line[0][0] + ',' + line[0][1] + '\n')
        write_file.writelines(rescontent)
        read_file.close()
    write_file.close()


def readlogfile(filepath, filename):
    '''
    
    Args:
        filepath: string: 完整的文件路径
        filename: string: 文件名，不包含文件名后缀

    Returns: dict: 字典，包含orignal、average、minimum、maxcimum三个DataFrame类型数据

    '''
    try:
        print("Evaluate log file: " + filename)
        dfs = pd.read_csv(
            filepath, sep=',', dtype={"Offset": np.str,
                                      "Hits": np.int64})
        offsets = dfs['Offset'].drop_duplicates().reset_index(drop=True)
        count = offsets.count()
        # print(offsets)
        # print(count)
        dfdave = pd.DataFrame({
            filename: pd.Series([0] * count),
            'Offset': offsets
        })
        dfdmin = pd.DataFrame({
            filename: pd.Series([0] * count),
            'Offset': offsets
        })
        dfdmax = pd.DataFrame({
            filename: pd.Series([0] * count),
            'Offset': offsets
        })
        # print(dfdave)
        # print(dfdave.columns)
        for offset in offsets:
            ls = dfs[dfs['Offset'] == offset]["Hits"]
            if len(ls) > 0:
                average = round(ls.mean())
                minvalue = ls.min()
                maxvalue = ls.max()
            else:
                average = 0
                minvalue = 0
                maxvalue = 0
            # varvalue = ls.var() 方差
            dfdave.loc[dfdave.Offset == offset, filename] = average
            dfdmin.loc[dfdmin.Offset == offset, filename] = minvalue
            dfdmax.loc[dfdmax.Offset == offset, filename] = maxvalue
        # print(dfdave)
        dfdave.reset_index(drop=True, inplace=True)
        dfdmin.reset_index(drop=True, inplace=True)
        dfdmax.reset_index(drop=True, inplace=True)
        dfdave = dfdave.set_index("Offset")
        dfdmax = dfdmax.set_index("Offset")
        dfdmin = dfdmin.set_index("Offset")
        return {
            "original": dfs,
            "average": dfdave,
            "maximum": dfdmax,
            "minimum": dfdmin
        }
    except Exception as ex:
        print(Exception, ex)
        traceback.print_exc()
        return None


def dowithlogfile(filepath, filename):
    '''
    do with file
    '''
    tmp_file_path = config.TMP_FILE_PATH
    pretreatment(filepath, tmp_file_path)
    res = readlogfile(tmp_file_path, filename)
    os.remove(tmp_file_path)
    return res


if __name__ == "__main__":
    # dowithlogfile("../data/a.log",'a')
    print(dowithlogfile("../data/a.log", "a"))
