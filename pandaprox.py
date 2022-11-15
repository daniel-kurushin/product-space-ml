import numpy as np
import pandas as pd

boats = pd.ExcelFile("boats.xlsx")
boat_prices = boats.parse('Лист1')

D = np.hstack((boat_prices.values[:,1:5], 
               boat_prices.values[:,6:7]) ).astype(np.double)
Y = boat_prices.values[:,5:6].astype(np.int32).flatten()

for i in range(len(D[0])):
    a, b = np.polyfit(
        np.sort(D[:,i]),
        np.linspace(0,1,len(D[:,i])),1
    )
    D[:,i] = D[:,i] * a + b

X = D.sum(axis=1)

a, b = np.polyfit(X, Y, 1)

for x, y in zip(X, Y):
	print(y, x*a + b)