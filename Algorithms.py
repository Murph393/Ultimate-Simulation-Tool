
# coding: utf-8

# In[22]:


import numpy as np
import progressbar
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GridSearchCV


# ### Select Best SVR Model

# In[23]:


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


# In[ ]:


def SVR_predict(estimators, data):  # data.type = list
    result = []
    data = np.array(data).reshape(1,-1)
    for estimator in estimators:
        result.append(estimator.predict(data))
    return result


# ### Select Best Random Forest Model
