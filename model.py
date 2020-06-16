import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import math
import pickle
import sklearn
from sklearn.ensemble import GradientBoostingRegressor
  

#load data to predict ST price
path='ST.csv'
file=pd.read_csv(path)
data=pd.DataFrame(file,columns=['age','overall','potential','pace','shooting','physic','attacking_finishing','attacking_heading_accuracy',
                            'movement_sprint_speed','movement_balance','power_shot_power'])
price=pd.DataFrame(file,columns=['value_eur'])

#load data to predict CB price
file3=pd.read_csv('cb.csv')
cbdata=pd.DataFrame(file3,columns=['age','overall','potential','defending','physic','defending_standing_tackle','defending_sliding_tackle','defending_marking',
                             'attacking_heading_accuracy','power_strength'])
cbprice=pd.DataFrame(file3,columns=['value_eur'])

#load data to predict CB potential
cbdata2=pd.DataFrame(file3,columns=['age','overall','defending','physic','defending_standing_tackle','defending_sliding_tackle','defending_marking',
                             'attacking_heading_accuracy','power_strength'])
cbpotential=pd.DataFrame(file3,columns=['potential'])

#load data to predict ST potential
path2='Book1.csv'
file2=pd.read_csv(path2,encoding= 'unicode_escape')
data2=pd.DataFrame(file2,columns=['age','overall','pace','shooting','physic','attacking_finishing','attacking_heading_accuracy',
                            'movement_sprint_speed','movement_balance','power_shot_power'])
potential=pd.DataFrame(file2,columns=['potential'])

#Solve st price problem
X=np.array(data)
Y=np.array(price)


X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.33,random_state=7)
#for i in range(100,200,10):
  #print("n_estimator:",i)

#print(Y_test)
#pickle.dump(model, open('model.pkl','wb'))

#Solve cb price problem
cbX=np.array(cbdata)
cbY=np.array(cbprice)
cbX_train,cbX_test,cbY_train,cbY_test=train_test_split(cbX,cbY,test_size=0.33,random_state=7)
cbmodel=GradientBoostingRegressor()
cbmodel.fit(cbX_train,cbY_train)
#pickle.dump(cbmodel, open('cbmodel.pkl','wb'))
#print(cbmodel.score(cbX_test,cbY_test))

#Solve st potential problem
X2=np.array(data2)
Y2=np.array(potential)
data2_train,data2_test,poten_train,poten_test=train_test_split(X2,Y2,test_size=0.25,random_state=7)
model2=GradientBoostingRegressor()
model2.fit(data2_train,poten_train)


params = {'n_estimators': 500,
          'max_depth': 4,
          'min_samples_split': 5,
          'learning_rate': 0.015,
          'loss': 'ls'}

model=GradientBoostingRegressor(**params)
model.fit(X_train,Y_train)

test_score = np.zeros((params['n_estimators'],), dtype=np.float64)
for i, y_pred in enumerate(model2.staged_predict(data2_test)):
    test_score[i] = model.loss_(poten_train, model2.predict(data2_train))

fig = plt.figure(figsize=(6, 6))
plt.subplot(1, 1, 1)
plt.title('Deviance')
plt.plot(np.arange(params['n_estimators']) + 1, model.train_score_, 'b-',
         label='Training Set Deviance')
plt.legend(loc='upper right')
plt.xlabel('Boosting Iterations')
plt.ylabel('Deviance')
fig.tight_layout()
plt.show()


print(model.score(X_test,Y_test))
mse = sklearn.metrics.mean_squared_error(model.predict(X_test),Y_test)
rmse=math.sqrt(mse)
print(mse,rmse)

#print(model2.predict(data2_test))
#pickle.dump(model2, open('model2.pkl','wb'))

#print(model2.score(data2_test,poten_test))


#solve cb potential problem
cbX2=np.array(cbdata2)
cbY2=np.array(cbpotential)
cbdata2_train,cbdata2_test,cbpoten_train,cbpoten_test=train_test_split(cbX2,cbY2,test_size=0.25,random_state=7)
cbmodel2=GradientBoostingRegressor()
cbmodel2.fit(cbdata2_train,cbpoten_train)
#pickle.dump(cbmodel2, open('cbmodel2.pkl','wb'))
#print(cbmodel2.score(cbdata2_test,cbpoten_test))
