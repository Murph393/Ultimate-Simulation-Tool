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


#GenRandParaTable(20, a=[1,3.4],b=[3,4])

