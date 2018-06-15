
# coding: utf-8

# ## Generate Random Parameter Table

# In[1]:

import numpy as np
def GenRandParaTable(number, **paras):
    with open("para_table.txt","w") as f:
        f.truncate()
    with open("para_table.txt","a") as f:
        for key in paras.keys():
            f.write(key+' ')
        f.write('\n')
        for i in range(number):
            for r in paras.values():
                f.write(str(round((r[1]-r[0])*np.random.rand()+r[0], 2))+' ')
            f.write('\n')


# ## Data Preprocess

# In[2]:

import pandas as pd
import shutil 
import sqlite3
import re

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


# ## Alogorithms

# * Support Vector Machine

# In[3]:

import progressbar
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV

def Select_Best_SVR_Model(data, label, degree, window, p_bar):
    data_train, data_test, label_train, label_test = train_test_split(data, label, test_size=0.2, random_state=16)
    
    instances = label_train.columns.size
    Estimators = []
    map = [1,2,3,4,6]
    degree = map[degree-1]

    C_dft = 100
    C_i = 10*int(10/degree)
    C = list(-np.array(range(0,C_dft,C_i))+C_dft)+[C_dft]+list(np.array(range(0,C_dft,C_i))+C_dft)
    C = list(set(C))
    ga_dft = 10
    ga_i = int(10/degree)
    gamma = list(-np.array(range(0,ga_dft,ga_i))+ga_dft)+[ga_dft]+list(np.array(range(0,ga_dft,ga_i))+ga_dft)
    gamma = list(set(gamma))
    
    progress = progressbar.ProgressBar(redirect_stdout = True)
    progress.start(instances)
    p_bar['maximum'] = instances
    p_bar['value'] = 0
    svr_paras = {'kernel':['rbf'], 'C': C, 'gamma': gamma}
    
    ##---Calculate estimators---##
    for i in range(instances):
        grid_search_cv = GridSearchCV(SVR(), svr_paras, n_jobs=1, verbose=0)
        grid_search_cv.fit(data_train, label_train.iloc[:,i])
        Estimators.append(grid_search_cv.best_estimator_)
        progress.update(i+1)
        p_bar['value']+=1
        window.update()
    progress.finish()

    ##---Calculate MSE---##
    data_pred = np.zeros_like(label_test)
    i=0
    for estimator in Estimators:
        data_pred[:,i] = estimator.predict(data_test)
        i=i+1
    MSE = mean_squared_error(label_test, data_pred)
    return MSE, Estimators

def SVR_predict(estimators, data):  # data.type = list
    result = []
    data = np.array(data).reshape(1,-1)
    for estimator in estimators:
        result.append(estimator.predict(data))
    return result


# * K-Nearest Neighbor

# In[4]:

from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import GridSearchCV

def Select_Best_KNN_Model(data, label, p_bar):
    p_bar['maximum'] = 1
    p_bar['value'] = 0
    
    knn_paras = {'n_neighbors':[2,3,4,5,6,7,8,9,10]}
    
    grid_search_cv = GridSearchCV(KNeighborsRegressor(), knn_paras,scoring='neg_mean_squared_error', n_jobs=1)
    grid_search_cv.fit(data,label)
    estimator = grid_search_cv.best_estimator_
    
    MSE = -grid_search_cv.best_score_
    p_bar['value']+=1
    
    return MSE,estimator

def KNN_predict(estimator, data):
    data = np.array(data).reshape(1,-1)
    return estimator.predict(data).flatten()


# * Random Forest

# In[5]:

from sklearn.ensemble import RandomForestRegressor

def Select_Best_RF_Model(data, label, p_bar):
    p_bar['maximum'] = 1
    p_bar['value'] = 0
    
    rf_paras = {'n_estimators':[200]}
    
    grid_search_cv = GridSearchCV(RandomForestRegressor(), rf_paras,scoring='neg_mean_squared_error', n_jobs=1)
    grid_search_cv.fit(data,label)
    estimator = grid_search_cv.best_estimator_
    
    MSE = -grid_search_cv.best_score_
    p_bar['value']+=1
    
    return MSE,estimator

def RF_predict(estimator, data):
    data = np.array(data).reshape(1,-1)
    return estimator.predict(data).flatten()


# # MAINLOOP

# In[6]:

import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from sklearn.neighbors import NearestNeighbors

SVR_estimators = [] #测试用，避免被删除
KNN_estimator = []
RF_estimator = []
data = []
label = []
MSE = 0
neigh = []
x_min,x_max,y_min,y_max = 0,0,0,0  #plot axis


# In[7]:

###---------------------------------------------------------------------------------------------------------------------------------------###
window = tk.Tk()
window.title('ULTIMATE SIMULATION TOOL')
window.geometry('1000x500')

###-----PREDEFINE-----###
font_step = ('Georgia', 14, 'italic')
font_argu = ('Microsoft Yahei', 12)
font_help = ('Microsoft Yahei', 10)
First_Train = True

scales = []

###-----PROGRESS_BAR-----###
p1 = ttk.Progressbar(window, length=350, mode="determinate", orient='horizontal')  
p1.place(x=600, y=380) 

###-----STEP 1-----###
s1_l1_text = 'STEP 1'
s1_l1 = tk.Label(window, text=s1_l1_text,font=font_step,bg='lightgreen').place(x=80, y=10)
s1_l2_text = '<终极仿真工具>\n第一次使用请根据\nREADME.md\n文件指引操作- -'
s1_l2 = tk.Label(window, text=s1_l2_text,font=font_argu,justify=tk.CENTER).place(x=40, y=45)

###-----STEP 2-----###
s2_l1_text = 'STEP 2'
s2_l1 = tk.Label(window, text=s2_l1_text,font=font_step,bg='lightgreen').place(x=80, y=150)
s2_l2_text = '<生成随机参数表>'
s2_l2 = tk.Label(window, text=s2_l2_text,font=font_argu,justify=tk.LEFT).place(x=45, y=185)
s2_l3_text = '仿真次数：'
s2_l3 = tk.Label(window, text=s2_l3_text,font=font_argu,justify=tk.LEFT).place(x=10, y=220)
s2_l4_text = '参数范围：'
s2_l4 = tk.Label(window, text=s2_l4_text,font=font_argu,justify=tk.LEFT).place(x=10, y=250)
s2_l5_text = '参数范围输入格式：\n参数名1=[min,max],参数名2=[...'
s2_l5 = tk.Label(window, text=s2_l5_text,font=font_help,
                 justify=tk.LEFT).place(x=15, y=275)
s2_l6_text = 'CST-->parameter sweep-->import-->\ndefine multiple sequences-->\n选择生成的para_table.txt文件-->ok'
s2_l6 = tk.Label(window, text=s2_l6_text,font=font_help,
                 justify=tk.LEFT).place(x=15, y=350)
s2_l7_text = '在点击start仿真之前,必须把需要观察的结\n果保存在template based postprocessing中\n,即使是S参数也需要用此方法复制一份结果.'
s2_l7 = tk.Label(window, text=s2_l7_text,font=font_help,
                 justify=tk.LEFT,bg='yellow').place(x=15, y=415)
s2_var1 = tk.StringVar()
s2_l8_text = tk.Label(window, textvariable=s2_var1,font=font_argu,bg='yellow',width=6).place(x=165, y=320)

s2_e1 = ttk.Entry(window,width=5)
s2_e1.place(x=100, y=223)
s2_e1.insert(tk.END,'250')
s2_e2 = ttk.Entry(window)
s2_e2.place(x=100, y=253)
s2_e2.insert(tk.END,'h2=[0.8,1],h3=[0.5,1],t1=[0.7,1.2],t2=[1.1,1.9]')
    
def s2_b1_func():
    try:
        var1 = int(s2_e1.get())
        var2 = s2_e2.get()
        eval('GenRandParaTable(var1, '+var2+')')
        with open('temp_paras.txt','w') as f:
            f.write(var2)
    except:
        s2_var1.set('失败！')
    else:
        s2_var1.set('完成！')
    
s2_b1 = ttk.Button(window,text="生成",width=10,command=s2_b1_func).place(x=80,y=320)

###-----STEP 3-----###
s3_l1_text = 'STEP 3'
s3_l1 = tk.Label(window, text=s3_l1_text,font=font_step,bg='lightgreen').place(x=300, y=10)
s3_l2_text = '<导出结果- ->'
s3_l2 = tk.Label(window, text=s3_l2_text,font=font_argu).place(x=290, y=40)
s3_l3_text = 'CST-->\nNavigation Tree-->\nTables-->\n选择需要训练的结果-->\nPost Processing-->\nImport/Export-->\nPlot Data(ASCII)-->\n命名为< 1.txt >'
s3_l3 = tk.Label(window, text=s3_l3_text,font=font_help,justify=tk.LEFT).place(x=260, y=65)
s3_l4_text = '进入STEP 4前确保1.txt与\n此文件处于同一根目录下！'
s3_l4 = tk.Label(window, text=s3_l4_text,font=font_help,
                 justify=tk.LEFT,bg='yellow').place(x=260, y=220)
s3_l5_text = 'STEP 4'
s3_l5 = tk.Label(window, text=s3_l5_text,font=font_step,bg='lightgreen').place(x=300, y=270)
s3_l6_text = '<选择一个算法>'
s3_l6 = tk.Label(window, text=s3_l6_text,font=font_argu).place(x=290, y=300)
s3_var3 = tk.StringVar()  #MSE
s3_var3.set('MSE:')
s3_l7 = tk.Label(window, textvariable=s3_var3,font=font_argu).place(x=600, y=350)
s3_l8_text = '<蓝色：预测曲线><橙色：最邻近实际曲线>'
s3_l8 = tk.Label(window, text=s3_l8_text,font=font_argu).place(x=600, y=410)
s3_var4 = tk.StringVar()  #nearest neighbor
s3_var4.set('最邻近参数：')
s3_l9 = tk.Label(window, textvariable=s3_var4,font=font_argu).place(x=600, y=435)

s3_var1 = tk.StringVar()  #执行情况信息
s3_l10 = tk.Label(window, textvariable=s3_var1,font=font_argu,bg='yellow',width=8).place(x=350, y=400)

s3_var2 = tk.StringVar()  #算法选择信息
s3_var2.set('KNN') #默认值

s3_c1 = ttk.Combobox(window,value=(1,2,3,4,5),width=2,state='readonly')
s3_c1.place(x=370,y=370)
s3_c1.current(0)

s3_r1 = ttk.Radiobutton(window, text='KNN',variable=s3_var2 ,value='KNN').place(x=300,y=330)
s3_r2 = ttk.Radiobutton(window, text='SVM',variable=s3_var2 ,value='SVM').place(x=300,y=370)
s3_r3 = ttk.Radiobutton(window, text='RF',variable=s3_var2 ,value='RF').place(x=300,y=350)

image = Figure(figsize=(5,4), dpi=80)
plot = image.add_subplot(111)
plot.plot([])
canvas =FigureCanvasTkAgg(image, master=window)
canvas.draw()
canvas.get_tk_widget().place(x=590,y=20)
def plot_data(useless):
    one_data = []
    for scaler in scales:
        one_data.append(scaler.get())
    if s3_var2.get() == 'SVM':
        result = SVR_predict(SVR_estimators, one_data)
    elif s3_var2.get() == 'KNN':
        result = KNN_predict(KNN_estimator, one_data)
    elif s3_var2.get() == 'RF':
        result = RF_predict(RF_estimator, one_data)

    plot.clear()
    plot.plot(label.columns,result,color='blue')
    nearest_neigh = neigh.kneighbors([one_data],return_distance=False).item()
    s3_var4.set('最邻近参数:'+str(data.iloc[nearest_neigh,:].tolist()))
    plot.plot(label.columns,label.iloc[nearest_neigh,:].tolist(),color='orange')
    if s3_var5.get() == True:
        plot.axis([x_min,x_max,y_min,y_max])
    canvas.draw()
    
def generate_scale(data):
    global scales
    min_sers = pd.Series(data.min()).to_dict()
    max_sers = pd.Series(data.max()).to_dict()
    i=0
    for key,min_v,max_v in zip(min_sers.keys(),min_sers.values(),max_sers.values()):
        scales.append(tk.Scale(window, label=key, from_=min_v, to=max_v, orient=tk.HORIZONTAL,
                     length=120, showvalue=1, resolution=0.01,command=plot_data))
        scales[i].place(x=450,y=i*59)
        i+=1

def s3_b1_func():
    global data, label, MSE, SVR_estimators,KNN_estimator,RF_estimator,    First_Train, neigh,x_min,x_max,y_min,y_max
    
    s3_var1.set('导入中。。')
    window.update()
    if First_Train:
        data,label = DataPreprocess()
        x_min = label.columns.min()
        x_max = label.columns.max()
        y_min = label.min().min()
        y_max = label.max().max()
        neigh = NearestNeighbors(n_neighbors=1)
        neigh.fit(data)
    
    s3_var1.set('计算中。。')
    window.update()
    if s3_var2.get() == 'SVM':
        MSE,SVR_estimators = Select_Best_SVR_Model(data,label,int(s3_c1.get()),window,p1)
    elif s3_var2.get() == 'KNN':
        MSE,KNN_estimator = Select_Best_KNN_Model(data, label, p1)
    elif s3_var2.get() == 'RF':
        MSE,RF_estimator = Select_Best_RF_Model(data, label, p1)
        
    s3_var1.set('完成！')
    window.update()
    
    s3_var3.set('MSE:'+str(MSE))
    #generate scales
    if First_Train:
        generate_scale(data)
        First_Train = False
    
s3_b1 = ttk.Button(window,text="训练",width=5,command=s3_b1_func).place(x=300,y=400)

s3_var5 = tk.BooleanVar()
s3_ch1 = ttk.Checkbutton(window, text='固定y轴',variable = s3_var5)
s3_ch1.place(x=900, y=350)

window.mainloop()


# In[ ]:



