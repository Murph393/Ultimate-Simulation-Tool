import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from Gen_Random_ParaTable import GenRandParaTable
from Data_Preprocess import DataPreprocess
from Algorithms import Select_Best_SVR_Model
from Algorithms import SVR_predict

estimators = [] #测试用，避免被删除
data = []
label = []
MSE = 0

window = tk.Tk()
window.title('ULTIMATE SIMULATION TOOL')
window.geometry('1000x500')

###-----PREDEFINE-----###
font_step = ('Georgia', 14, 'italic')
font_argu = ('Microsoft Yahei', 12)
font_help = ('Microsoft Yahei', 10)
First_Train = True

scales = []
algorm = 'SVM' ##缺少默认值

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
s3_l6 = tk.Label(window, textvariable=s3_var3,font=font_argu).place(x=600, y=350)

s3_var1 = tk.StringVar()  #执行情况信息
s3_l10 = tk.Label(window, textvariable=s3_var1,font=font_argu,bg='yellow',width=8).place(x=350, y=380)

s3_var2 = tk.StringVar()  #算法选择信息
s3_var2.set('Select_Best_SVR_Model') #默认值

s3_c1 = ttk.Combobox(window,value=(1,2,3,4,5),width=2,state='readonly')
s3_c1.place(x=370,y=330)
s3_c1.current(0)

def s3_r1_func():
    global algorm
    algorm = 'SVM'
s3_r1 = ttk.Radiobutton(window, text='SVR',variable=s3_var2, value='Select_Best_SVR_Model',
                       command=s3_r1_func).place(x=300,y=330)

image = Figure(figsize=(5,4), dpi=80)
plot = image.add_subplot(111)
plot.plot([])
canvas =FigureCanvasTkAgg(image, master=window)
canvas.draw()
canvas.get_tk_widget().place(x=590,y=20)
def plot_data(useless):
    data = []
    for scaler in scales:
        data.append(scaler.get())
    if algorm == 'SVM':
        result = SVR_predict(estimators, data)
    plot.clear()
    plot.plot(label.columns,result)
    canvas.draw()
def generate_scale(**paras):
    global scales
    i=0
    for key, value in paras.items():
        scales.append(tk.Scale(window, label=key, from_=value[0], to=value[1], orient=tk.HORIZONTAL,
                     length=120, showvalue=1, resolution=0.01,command=plot_data))
        scales[i].place(x=450,y=i*59)
        i+=1

def s3_b1_func():
    global data, label, MSE, estimators, First_Train
    s3_var1.set('导入中。。')
    window.update()
    if First_Train:
        data,label = DataPreprocess()
    s3_var1.set('计算中。。')
    window.update()
    MSE,estimators = eval(s3_var2.get()+'(data,label,'+s3_c1.get()+',window,p1)')
    s3_var1.set('完成！')
    window.update()
    s3_var3.set('MSE:'+str(MSE))
    #generate scales
    if First_Train:
        with open('temp_paras.txt','r') as f:
            paras = f.read()
        eval('generate_scale('+paras+')')
        First_Train = False
    
s3_b1 = ttk.Button(window,text="训练",width=5,command=s3_b1_func).place(x=300,y=380)

window.mainloop()