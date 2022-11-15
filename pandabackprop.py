from sklearn.neural_network import MLPClassifier

import numpy as np
import pandas as pd

boats = pd.ExcelFile("boats.xlsx")
boat_prices = boats.parse('Лист1')

D = np.hstack((boat_prices.values[:,1:5], 
               boat_prices.values[:,6:7]) ).astype(np.double)
Y0 = boat_prices.values[:,5:6].astype(np.int32).flatten()

HP = sorted(set(Y0))

for i in range(len(D[0])):
    a, b = np.polyfit(np.sort(D[:,i]),np.linspace(0,1,len(D[:,i])),1)
    D[:,i] = D[:,i] * a + b

Y = np.zeros((len(Y0), len(HP)))
for i, y0 in zip(range(len(Y0)), Y0):
    Y[i,HP.index(y0)] = 1.0

clf = MLPClassifier(
    solver='lbfgs', 
    alpha=1e-5,
    hidden_layer_sizes=(200), 
    random_state=1,
    max_iter=100, 
    warm_start=True
)

for x in range(100):
    clf.fit(D, Y)

Y_ = clf.predict_proba(D)

for a, b in zip(Y, Y_):
    print("Y :", [ round(x) for x in a ], "> Y':", [ round(x) for x in b ])