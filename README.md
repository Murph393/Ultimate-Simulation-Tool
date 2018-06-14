
# Ultimate Simlulation Tool

## 简介(Brief Introduction)：

这是一个数据处理工具  
利用CST仿真的部分结果数据(离散)，去预测所有结果(连续)，free your mind~  
效果如下图：

![avatar](https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1529500444&di=56373d9334a5b5c1ad1c3077daf3cb0d&imgtype=jpg&er=1&src=http%3A%2F%2Fimg.zcool.cn%2Fcommunity%2F012b275930ff3ba8012193a349e497.gif)

## 如何使用？(How to play?)

第一次使用：下载OST.py; run.bat; install.bat三个文件  
(此程序默认你已经安装3.x版本python)  
1.双击install.bat 安装需要的python相关Support packages  
2.确保OST.py; run.bat处于同一文件夹下  
3.双击运行run.bat即可(也可使用任意其他运行py脚本的方式使用OST.py)  
主界面如下  
![avatar](https://ss2.bdstatic.com/70cFvnSh_Q1YnxGkpoWK1HF6hhy/it/u=171210280,1980212386&fm=27&gp=0.jpg)

## 详细说明(TL;DR)

(如果你没有意外地成功打开了这个脚本的话~)

* STEP 1  
 (稍微详细一点的介绍) 一个未知的CST模型，想知道参数对结果的影响，用了这个软件，不需要手动调整参数，能做的只需要挂机就可以了。

* STEP 2  
 <生成随机参数表>  
 why: CST不支持随机参数扫描，而为了均匀地获取所有参数的信息，随机参数扫描是必须的。  
 how: 在本脚本中，设置仿真次数(即生成多少组随机参数)，根据模型的复杂度，推荐设置越高越好，根据模型复杂度，250组可能要跑24h，但是在有足够的数据后，可以随时停下CST的仿真进程，参数范围请严格根据脚本中解释的格式设置，参数名需要严格符合CST中的参数名字(大小写)；在CST中的操作本脚本上有详细的介绍。  
 what: 利用CST parameter sweep功能中的import功能可以自定义参数组合的原理实现的。点击生成且显示成功后，会在脚本同目录下生成一个para_table.txt文件，CST中import该文件即可。

* STEP 2.5  
 现在就可以在CST中点击start开始仿真了，但务必把需要看的结果使用template based postprocessing 中保存。只有这样设置后，才能方便导出需要的结果，然后务必去睡大觉。

* STEP 3  
 <导出结果>  
 好了，看到CST停下来了(或者你不想等了/参数表设太大了，手动把CST仿真过程停止了)，在导航树中找到你想看的post processing结果，根据导引Export导出结果名为1.txt(别的名字识别不了)就ok了。  
 在CST模型的Result文件夹下有一个db.parmap文件，最后保证1.txt,db.parmap和这个脚本在同一个文件夹下，最后一步之前的所有就准备好了~ 

 >总结是很有必要的：`OST.py` ，`1.txt` 和`db.paramap` 三个文件必须处于同一目录下，推荐把OST.py放到仿真结果的Result文件夹下。

* STEP 4  
 <训练>  
 就像开始所说的，准备好所有需要的数据后，最后一步就是利用CST计算出的少量结果，通过一定算法去预测所有结果。  
 `其实直接点击训练按钮就可以了。`会及时提示正在导入数据-->正在训练-->成功！  

## 简单说一下算法：  

* SVM(Support Vector Machine)，支持向量机  

    右边的下拉框与复杂度有关，选择越高的值可以获得略微更好的结果，但运算时间会指数上升。建议不需要尝试训练4或者5阶的结果。

* RF(Random Forest)，随机森林

    对复杂的结果有较好的结果，至少不会估计错已有的结果，但这个功能还没有做好。  

* Knn(K-nearest neighbors)，k阶近邻  

    对训练数据集较小的情况下有较好的结果，这个功能还没有做好。

* DNN(Deep Neural Network)，深度神经网络  

    不存在的~

  MSE(Mean Square Error)，用于参考算法的性能，越小说明结果越好。  

## 其他一些重要的事情(Matters)

* 如果窗口未响应，并不是真的卡了，只是因为某些原因未及时刷新窗口代码，比如导入数据时或者选择了高阶数的SVM算法训练时。
