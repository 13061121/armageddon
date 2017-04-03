'''
处理评估数据
'''

import os
import re
import pandas as pd
import dataresolve as dr


def addtable(datatable, data):
    '''
    合并单元表格
    '''
    if datatable is None:
        return data
    else:
        # return pd.concat([datatable, data], axis=1)
        return pd.merge(datatable,data,how="outer",on="Offset",left_index=False,right_index=False,copy=True)


def getdatas(dirpath):
    datatable = None
    filelist = os.listdir(dirpath)
    fpattern = re.compile(r'(.+)\.log')
    for file in filelist:
        filepath = dirpath + '/' + file
        if os.path.isdir(filepath):
            continue
        filename = fpattern.match(file).group(1)
        # print(filename)
        if os.path.isfile(filepath):
            data = dr.dowithlogfile(filepath, filename)
            datatable = addtable(datatable, data)
    return datatable.fillna(0)


if __name__ == "__main__":
    # print(getdatas("/home/larry/Documents/armageddon/makeMatrix/data"))
    datas = getdatas("/home/larry/Documents/log")
    print(datas)
    datas.to_csv("/home/larry/Documents/log/res/res.log")