import numpy as np
import pandas as pd
import shutil 
import sqlite3

import re
import matplotlib as plt

def DataPreprocess():
    shutil.copyfile('db.parmap','parmap.db') #copy and rename

    with sqlite3.connect('parmap.db') as con:
        ParaList = pd.read_sql("SELECT * FROM ParaList", con=con)
        ParaCombinations = pd.read_sql("SELECT * FROM ParaCombinations", con=con)
    ParaCombinations.columns = ['combi_id']+ParaList['name'].tolist()
    
    ColumnIndex = []
    skip = 0
    with open('1.txt') as txtData:
        lines = txtData.readlines()
        for line in lines:
            if ((line.find('run') != -1) or (line.find('--') != -1) or line == '\n'):
                if skip == 2:
                    break
                skip += 1
                continue
            ColumnIndex.append(np.float64(line.split()[0]))
    RowIndex = []
    with open('1.txt') as txtData:
        lines = txtData.readlines()
        for line in lines:
            if line.find('run') != -1:
                line = re.sub("\D",'',line)
                RowIndex.append(int(line))
    LabelMatrix = np.zeros((len(RowIndex)* len(ColumnIndex)))
    LabelMatrix.shape
    i = 0
    with open('1.txt') as txtData:
        lines = txtData.readlines()
        for line in lines:
            if ((line.find('run') == -1) and (line.find('--') == -1) and line != '\n'):
                LabelMatrix[i] = np.float64(line.split()[1])
                i += 1
    LabelMatrix = LabelMatrix.reshape((len(RowIndex),len(ColumnIndex)))
    label = pd.DataFrame(LabelMatrix, RowIndex, ColumnIndex)
    
    data = pd.DataFrame(np.zeros((len(RowIndex), len(ParaList['name']))),                       RowIndex, ParaList['name'])
    
    for i in RowIndex:
        for j, row in ParaCombinations.iterrows():
            if i == row['combi_id']:
                data.loc[i] = row
                break
    for col in data.columns:
        data_temp = data.loc[RowIndex[0], col]
        for row in RowIndex:
            if data_temp != data.loc[row, col]:
                break
            if row == RowIndex[-1]:
                del data[col]
    return data, label

